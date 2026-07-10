/**
 * SmartArena AI — Salt Lake Stadium Map Module
 * =============================================
 *
 * Renders a Google Maps satellite view of Vivekananda Yuba Bharati
 * Krirangan (Salt Lake Stadium), Kolkata, with interactive gate
 * markers color-coded by live status.
 *
 * Default ground: Salt Lake Stadium
 *   Centre: 22.5680° N, 88.4055° E
 *   Zoom:   17 (clearly shows ring structure)
 */

/* global google, CONFIG, fetch */

const StadiumMap = (() => {
  // ── Stadium Constants ────────────────────────────────────────────────
  const STADIUM_CENTER = { lat: 22.5680, lng: 88.4055 };
  const STADIUM_ZOOM = 17;
  const STADIUM_NAME = 'Vivekananda Yuba Bharati Krirangan (Salt Lake Stadium)';

  // ── Gate Configuration ───────────────────────────────────────────────
  // Positions are approximated on the stadium's elliptical perimeter.
  // Salt Lake Stadium is ~300 m (N-S) x ~250 m (E-W).  Markers are
  // placed at roughly equal angular intervals using parametric ellipse
  // equations with semi-axes a = 125 m (E-W), b = 150 m (N-S).
  //
  // Conversion factors at 22.57°N:
  //   1° latitude  ≈ 111 000 m
  //   1° longitude ≈ 102 500 m  (111 000 × cos 22.57°)
  //
  // Gate numbering starts at the north and proceeds clockwise.

  const DEG_LAT_PER_M = 1 / 111000;
  const DEG_LNG_PER_M = 1 / 102500;
  const SEMI_MAJOR_M = 125; // east–west radius (metres)
  const SEMI_MINOR_M = 150; // north–south radius (metres)

  // Raw angle → {lat, lng} on the ellipse
  function gatePosition(angleDeg) {
    const rad = (angleDeg * Math.PI) / 180;
    const dx = SEMI_MAJOR_M * Math.cos(rad); // east positive
    const dy = SEMI_MINOR_M * Math.sin(rad); // north positive
    return {
      lat: STADIUM_CENTER.lat + dy * DEG_LAT_PER_M,
      lng: STADIUM_CENTER.lng + dx * DEG_LNG_PER_M,
    };
  }

  /**
   * Eight gates placed at 45° intervals around the elliptical perimeter.
   * Positions match the real stadium's general layout as visible in
   * satellite imagery (gate names may vary for different events).
   */
  const GATES = [
    { id: 'gate-1', name: 'Gate 1 (North)',          angle: 90,  capacity: 5000 },
    { id: 'gate-2', name: 'Gate 2 (North-East)',      angle: 45,  capacity: 3500 },
    { id: 'gate-3', name: 'Gate 3 (East)',            angle: 0,   capacity: 5000 },
    { id: 'gate-4', name: 'Gate 4 (South-East)',      angle: 315, capacity: 3500 },
    { id: 'gate-5', name: 'Gate 5 (South)',           angle: 270, capacity: 5000 },
    { id: 'gate-6', name: 'Gate 6 (South-West)',      angle: 225, capacity: 3500 },
    { id: 'gate-7', name: 'Gate 7 (West)',            angle: 180, capacity: 5000 },
    { id: 'gate-8', name: 'Gate 8 (North-West)',      angle: 135, capacity: 3500 },
  ].map((g) => ({ ...g, position: gatePosition(g.angle) }));

  // ── Status Colour Mapping ────────────────────────────────────────────
  const STATUS_COLORS = {
    open:       { fill: '#00ff88', stroke: '#00cc66', label: 'Open' },
    closed:     { fill: '#ef4444', stroke: '#cc2222', label: 'Closed' },
    maintenance:{ fill: '#eab308', stroke: '#b8960a', label: 'Maintenance' },
  };

  const FALLBACK_STATUS = 'open'; // default when API is unreachable

  // ── Module State ─────────────────────────────────────────────────────
  let map = null;
  let gateMarkers = [];        // { marker, gate, infoWindow }
  let gateStatusCache = {};    // gateId → 'open' | 'closed' | 'maintenance'
  let statusPollTimer = null;
  let onLoadCallback = null;

  // ── Dynamic Map-Loading Promise ──────────────────────────────────────
  let _mapsPromise = null;

  function _loadMapsApi() {
    if (_mapsPromise) return _mapsPromise;

    _mapsPromise = new Promise((resolve, reject) => {
      const apiKey = CONFIG.GOOGLE_MAPS_API_KEY;
      if (!apiKey || apiKey === 'YOUR_GOOGLE_MAPS_API_KEY') {
        reject(new Error('Google Maps API key not configured'));
        return;
      }

      // If the Google Maps JS API is already loaded, resolve immediately
      if (typeof google !== 'undefined' && google.maps) {
        resolve();
        return;
      }

      window.__initStadiumGoogleMap = () => resolve();
      const script = document.createElement('script');
      script.src =
        `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}` +
        '&libraries=places&callback=__initStadiumGoogleMap';
      script.async = true;
      script.defer = true;
      script.onerror = () => reject(new Error('Failed to load Google Maps JS API'));
      document.head.appendChild(script);
    });

    return _mapsPromise;
  }

  // ── Gate Status Fetching ─────────────────────────────────────────────

  async function fetchGateStatus() {
    try {
      const res = await fetch(CONFIG.apiUrl('/admin/gates'), {
        credentials: 'include',
      });
      if (!res.ok) return;
      const json = await res.json();
      const gates = json.data?.gates || [];
      gates.forEach((g) => {
        const normalised = (g.name || '').replace(/\s+/g, ' ').trim().toLowerCase();
        GATES.forEach((gate) => {
          const gateNorm = gate.name.replace(/\s+/g, ' ').trim().toLowerCase();
          if (normalised === gateNorm || normalised.includes(gate.id)) {
            gateStatusCache[gate.id] = g.status || FALLBACK_STATUS;
          }
        });
      });
    } catch {
      // Silently fall back to defaults — the API may require auth
    }
  }

  // ── Marker Helpers ───────────────────────────────────────────────────

  function _gateStatus(gateId) {
    return gateStatusCache[gateId] || FALLBACK_STATUS;
  }

  function _buildInfoContent(gate, status) {
    const col = STATUS_COLORS[status] || STATUS_COLORS[FALLBACK_STATUS];
    return `
      <div style="font-family:Inter,sans-serif;color:#1e293b;padding:6px 10px;min-width:180px">
        <div style="font-weight:700;font-size:14px;margin-bottom:4px">${gate.name}</div>
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
          <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${col.fill}"></span>
          <span style="font-weight:600;font-size:13px">${col.label}</span>
        </div>
        <div style="font-size:12px;color:#64748b">Capacity: ${gate.capacity.toLocaleString()}</div>
      </div>`;
  }

  function _createMarker(gate) {
    const status = _gateStatus(gate.id);
    const col = STATUS_COLORS[status] || STATUS_COLORS[FALLBACK_STATUS];

    const marker = new google.maps.Marker({
      position: gate.position,
      map,
      title: gate.name,
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        scale: 10,
        fillColor: col.fill,
        fillOpacity: 0.85,
        strokeColor: '#ffffff',
        strokeWeight: 2,
      },
      label: {
        text: gate.name.replace(/Gate\s*/i, 'G'),
        color: '#ffffff',
        fontSize: '9px',
        fontWeight: 'bold',
      },
    });

    const infoWindow = new google.maps.InfoWindow({
      content: _buildInfoContent(gate, status),
    });

    marker.addListener('click', () => infoWindow.open(map, marker));

    return { marker, gate, infoWindow };
  }

  function _updateMarkerColors() {
    gateMarkers.forEach(({ marker, gate, infoWindow }) => {
      const status = _gateStatus(gate.id);
      const col = STATUS_COLORS[status] || STATUS_COLORS[FALLBACK_STATUS];
      marker.setIcon({
        path: google.maps.SymbolPath.CIRCLE,
        scale: 10,
        fillColor: col.fill,
        fillOpacity: 0.85,
        strokeColor: '#ffffff',
        strokeWeight: 2,
      });
      infoWindow.setContent(_buildInfoContent(gate, status));
    });
  }

  // ── Public API ───────────────────────────────────────────────────────

  /**
   * Initialise the Google Map inside the given container element.
   *
   * @param {HTMLElement} container - DOM element to host the map.
   * @param {Function}   [onLoad]  - Optional callback fired after the map
   *                                  and markers are ready.
   * @returns {Promise<void>}
   */
  async function init(container, onLoad) {
    onLoadCallback = onLoad || null;

    try {
      await _loadMapsApi();
    } catch (err) {
      console.warn('[StadiumMap]', err.message);
      container.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full text-center p-8">
          <div class="text-4xl mb-4" aria-hidden="true">🗺️</div>
          <h3 class="text-lg font-bold text-white mb-2">Google Maps API Not Configured</h3>
          <p class="text-sm text-surface-200/60 mb-2">Add your Maps API key to enable the interactive map.</p>
          <p class="text-xs text-surface-200/40">Set VITE_GOOGLE_MAPS_API_KEY in frontend/.env</p>
        </div>`;
      return;
    }

    // Create the map
    map = new google.maps.Map(container, {
      center: STADIUM_CENTER,
      zoom: STADIUM_ZOOM,
      mapTypeId: 'satellite',
      mapTypeControl: true,
      mapTypeControlOptions: {
        style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
        position: google.maps.ControlPosition.TOP_RIGHT,
      },
      fullscreenControl: true,
      streetViewControl: false,
    });

    // Stadium centre label
    new google.maps.Marker({
      position: STADIUM_CENTER,
      map,
      title: STADIUM_NAME,
      icon: {
        path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
        scale: 5,
        fillColor: '#38bdf8',
        fillOpacity: 0.9,
        strokeColor: '#ffffff',
        strokeWeight: 1,
      },
      label: {
        text: 'STADIUM',
        color: '#ffffff',
        fontSize: '10px',
        fontWeight: 'bold',
      },
    });

    // Fetch live gate statuses then render markers
    await fetchGateStatus();
    gateMarkers = GATES.map(_createMarker);

    // Poll for status changes every 30 seconds
    statusPollTimer = setInterval(async () => {
      await fetchGateStatus();
      _updateMarkerColors();
    }, 30000);

    // Clean up on page unload
    window.addEventListener('pagehide', () => {
      if (statusPollTimer) clearInterval(statusPollTimer);
    });
    window.addEventListener('beforeunload', () => {
      if (statusPollTimer) clearInterval(statusPollTimer);
    });

    if (onLoadCallback) onLoadCallback(map);
  }

  /**
   * Force-refresh all gate marker colours (e.g. after an admin update).
   */
  async function refresh() {
    await fetchGateStatus();
    _updateMarkerColors();
  }

  /**
   * Pan the map to a specific gate.
   * @param {string} gateId - e.g. 'gate-1'
   */
  function focusGate(gateId) {
    const entry = gateMarkers.find((m) => m.gate.id === gateId);
    if (entry && map) {
      map.panTo(entry.gate.position);
      map.setZoom(19);
      google.maps.event.trigger(entry.marker, 'click');
    }
  }

  /**
   * Reset view to the default stadium overview.
   */
  function resetView() {
    if (map) {
      map.panTo(STADIUM_CENTER);
      map.setZoom(STADIUM_ZOOM);
    }
  }

  return {
    init,
    refresh,
    focusGate,
    resetView,
    STADIUM_CENTER,
    GATES,
  };
})();
