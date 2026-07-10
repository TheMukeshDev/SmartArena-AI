/**
 * SmartArena AI — Map Interactivity Logic
 * ==========================================
 *
 * Manages the SVG heatmap view and integrates with StadiumMap for the
 * Google Maps satellite view of Salt Lake Stadium, Kolkata.
 */

/* global CONFIG, Auth, initFirebase, showToast, StadiumMap */

// ── Stand Zones (SVG heatmap conceptual areas) ────────────────────────
const STADIUM_ZONES = [
  { name: 'North Stand', position: { lat: 22.5694, lng: 88.4055 } },
  { name: 'South Stand', position: { lat: 22.5666, lng: 88.4055 } },
  { name: 'West Stand', position: { lat: 22.5680, lng: 88.4043 } },
  { name: 'East Stand', position: { lat: 22.5680, lng: 88.4067 } },
];

let googleMap = null;
let zoneMarkers = [];
let currentView = 'google'; // default is Google Maps view
let zones = []; // SVG path elements, initialised in initMapPage

// ── Bootstrap ─────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  try {
    await initFirebase();
    Auth.initAuthListener(async (user) => {
      if (!user) {
        window.location.href = 'login.html';
        return;
      }
      initMapPage();
    });
  } catch (err) {
    console.error('Firebase init failed in map:', err);
  }
});

// ── Main Initialisation ───────────────────────────────────────────────

function initMapPage() {
  zones = document.querySelectorAll('path[data-zone]');

  // Panel Elements
  const emptyState = document.getElementById('zone-info-empty');
  const infoCard = document.getElementById('zone-info-card');
  const zoneNameEl = document.getElementById('panel-zone-name');
  const statusIndEl = document.getElementById('panel-status-indicator');
  const statusTextEl = document.getElementById('panel-status-text');
  const occupancyEl = document.getElementById('panel-occupancy');
  const headcountEl = document.getElementById('panel-headcount');
  const capacityEl = document.getElementById('panel-capacity');
  const progressEl = document.getElementById('panel-progress-bar');
  const insightEl = document.getElementById('panel-ai-insight');

  // View toggle buttons
  const viewHeatmapBtn = document.getElementById('view-heatmap');
  const viewGoogleBtn = document.getElementById('view-google');
  const stadiumMapSvg = document.getElementById('stadium-map');
  const googleMapDiv = document.getElementById('google-map');

  // ── Simulated Crowd Data ───────────────────────────────────────────

  const generateSimData = (zoneName) => {
    const capacity =
      zoneName === 'North Stand' || zoneName === 'South Stand' ? 15000 : 10000;
    const occupancyPct = Math.floor(Math.random() * 80) + 15;
    const headcount = Math.floor(capacity * (occupancyPct / 100));

    let status = 'Optimal';
    let color = '#00ff88';
    let aiInsight =
      'Crowd flow is stable. All concession stands operating normally.';
    let tailwindColor = 'bg-neon-green text-neon-green';

    if (occupancyPct >= 90) {
      status = 'Critical';
      color = '#ef4444';
      aiInsight =
        'Zone at max capacity! Redirecting incoming fans to alternative entrances. Dispatching extra security.';
      tailwindColor = 'bg-red-500 text-red-500';
    } else if (occupancyPct >= 75) {
      status = 'Congested';
      color = '#ff6b2b';
      aiInsight =
        'High density detected. Wait times for restrooms are exceeding 10 minutes.';
      tailwindColor = 'bg-neon-orange text-neon-orange';
    } else if (occupancyPct >= 50) {
      status = 'Moderate';
      color = '#eab308';
      aiInsight =
        'Filling up steadily. Pre-order kiosks seeing increased traffic.';
      tailwindColor = 'bg-yellow-500 text-yellow-500';
    }

    return {
      capacity,
      occupancyPct,
      headcount,
      status,
      color,
      aiInsight,
      tailwindColor,
    };
  };

  // ── Live Simulation Interval ───────────────────────────────────────

  const _mapInterval = setInterval(() => {
    zones.forEach((zone) => {
      const data = generateSimData(zone.dataset.zone);
      zone.setAttribute('fill', data.color + '80');
      zone.dataset.currentData = JSON.stringify(data);

      const label = `${zone.dataset.zone} zone, ${data.occupancyPct}% full, ${data.status}. Press Enter for details.`;
      zone.setAttribute('aria-label', label);
    });

    if (currentView === 'google' && googleMap) {
      updateGoogleMapMarkers();
    }
  }, 5000);

  window.addEventListener('pagehide', () => clearInterval(_mapInterval));
  window.addEventListener('beforeunload', () => clearInterval(_mapInterval));

  // ── Zone Selection (SVG heatmap) ───────────────────────────────────

  const selectZone = (zone) => {
    const data = JSON.parse(zone.dataset.currentData);

    emptyState.classList.add('hidden');
    infoCard.classList.remove('hidden');

    zoneNameEl.textContent = zone.dataset.zone;
    occupancyEl.textContent = `${data.occupancyPct}%`;
    occupancyEl.setAttribute(
      'aria-label',
      `Occupancy ${data.occupancyPct} percent`
    );
    headcountEl.textContent = data.headcount.toLocaleString();
    headcountEl.setAttribute(
      'aria-label',
      `Headcount ${data.headcount.toLocaleString()}`
    );
    capacityEl.textContent = data.capacity.toLocaleString();
    progressEl.style.width = `${data.occupancyPct}%`;
    progressEl.setAttribute('aria-valuenow', data.occupancyPct);
    insightEl.textContent = data.aiInsight;

    statusTextEl.textContent = data.status;
    statusIndEl.className =
      'w-2 h-2 rounded-full animate-pulse ' +
      data.tailwindColor.split(' ')[0];
    statusTextEl.className =
      'text-sm font-medium ' + data.tailwindColor.split(' ')[1];
    progressEl.className =
      'h-full rounded-full transition-all duration-500 ' +
      data.tailwindColor.split(' ')[0];

    zones.forEach((z) => {
      z.setAttribute('stroke-width', '2');
      z.setAttribute('aria-pressed', 'false');
    });
    zone.setAttribute('stroke-width', '4');
    zone.setAttribute('stroke', '#ffffff');
    zone.setAttribute('aria-pressed', 'true');
  };

  zones.forEach((zone) => {
    const initData = generateSimData(zone.dataset.zone);
    zone.dataset.currentData = JSON.stringify(initData);
    zone.setAttribute('aria-pressed', 'false');
    zone.setAttribute(
      'aria-label',
      `${zone.dataset.zone} zone, ${initData.occupancyPct}% full, ${initData.status}. Press Enter for details.`
    );

    zone.addEventListener('click', () => selectZone(zone));
    zone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        selectZone(zone);
      }
    });
  });

  // ── View Toggle Logic ──────────────────────────────────────────────

  const switchView = (view) => {
    currentView = view;
    if (view === 'heatmap') {
      stadiumMapSvg.classList.remove('hidden');
      googleMapDiv.classList.add('hidden');
      document.getElementById('transport-overlay').classList.add('hidden');
      viewHeatmapBtn.classList.add('bg-arena-600', 'text-white');
      viewHeatmapBtn.classList.remove('bg-surface-700', 'text-surface-200');
      viewGoogleBtn.classList.remove('bg-arena-600', 'text-white');
      viewGoogleBtn.classList.add('bg-surface-700', 'text-surface-200');
    } else {
      stadiumMapSvg.classList.add('hidden');
      googleMapDiv.classList.remove('hidden');
      document.getElementById('transport-overlay').classList.remove('hidden');
      viewGoogleBtn.classList.add('bg-arena-600', 'text-white');
      viewGoogleBtn.classList.remove('bg-surface-700', 'text-surface-200');
      viewHeatmapBtn.classList.remove('bg-arena-600', 'text-white');
      viewHeatmapBtn.classList.add('bg-surface-700', 'text-surface-200');

      // Initialise Google Maps via StadiumMap module (first time only)
      if (!googleMap) {
        initGoogleMap();
      }
    }
  };

  viewHeatmapBtn.addEventListener('click', () => switchView('heatmap'));
  viewGoogleBtn.addEventListener('click', () => switchView('google'));

  // ── AI Crowd Analysis ──────────────────────────────────────────────

  const analyzeBtn = document.getElementById('ai-analyze-btn');
  const insightsBanner = document.getElementById('ai-global-insights');
  const globalStatus = document.getElementById('ai-global-status');
  const insightsList = document.getElementById('ai-insights-list');
  const routingAdvice = document.getElementById('ai-routing-advice');
  const recommendedAction = document.getElementById('ai-recommended-action');

  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', async () => {
      analyzeBtn.disabled = true;
      analyzeBtn.innerHTML =
        '<span aria-hidden="true">🧠</span> Analyzing...';
      analyzeBtn.setAttribute('aria-busy', 'true');
      insightsBanner.classList.add('hidden');

      const zonesData = Array.from(zones).map((z) => {
        const d = JSON.parse(z.dataset.currentData);
        return {
          zone: z.dataset.zone,
          occupancy: d.occupancyPct,
          headcount: d.headcount,
        };
      });

      try {
        const res = await fetch(CONFIG.apiUrl('/ai/crowd/analyze'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ zones: zonesData }),
          credentials: 'include',
        });

        const data = await res.json();
        if (res.ok) {
          const analysis = data.data;
          globalStatus.textContent = analysis.global_status;

          insightsList.innerHTML = '';
          analysis.insights.forEach((insight) => {
            const li = document.createElement('li');
            li.textContent = insight;
            insightsList.appendChild(li);
          });

          routingAdvice.textContent =
            'Routing Advice: ' + analysis.routing_advice;

          if (analysis.predicted_status_15min) {
            const predEls = document.querySelectorAll('.zone-prediction');
            predEls.forEach((el) => el.remove());
            for (const [zoneName, status] of Object.entries(
              analysis.predicted_status_15min
            )) {
              const zoneEl = document.querySelector(
                `path[data-zone="${zoneName}"]`
              );
              if (zoneEl) {
                const trendEl = document.createElementNS(
                  'http://www.w3.org/2000/svg',
                  'title'
                );
                trendEl.className = 'zone-prediction';
                trendEl.textContent = `\u2192 ${status} in 15min`;
                zoneEl.appendChild(trendEl);
                zoneEl.dataset.predicted15 = status;
              }
            }
          }
          if (analysis.recommended_action && recommendedAction) {
            recommendedAction.textContent = analysis.recommended_action;
            recommendedAction
              .closest('.flex')
              ?.classList.remove('hidden');
          }
          insightsBanner.classList.remove('hidden');
        } else {
          showToast('AI failed to analyze crowd data.', 'error');
        }
      } catch (err) {
        console.error(err);
        showToast('Error contacting AI service.', 'error');
      } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML =
          '<span aria-hidden="true">🧠</span> Run AI Crowd Analysis';
        analyzeBtn.removeAttribute('aria-busy');
      }
    });
  }
}

// ── Google Maps Integration (via StadiumMap module) ────────────────────

function initGoogleMap() {
  const mapDiv = document.getElementById('google-map');

  StadiumMap.init(mapDiv, (map) => {
    googleMap = map;

    // Build zone markers from STADIUM_ZONES for the heatmap panel sync
    STADIUM_ZONES.forEach((zone) => {
      const marker = new google.maps.Marker({
        position: zone.position,
        map: googleMap,
        title: zone.name,
        visible: false, // hidden — gate markers from StadiumMap are the primary UI
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 12,
          fillColor: '#00ff88',
          fillOpacity: 0.8,
          strokeColor: '#ffffff',
          strokeWeight: 2,
        },
      });
      zoneMarkers.push({ marker, zone: zone.name });
    });

    loadTransportSuggestions();
  });
}

function updateGoogleMapMarkers() {
  zones.forEach((zone) => {
    const data = JSON.parse(zone.dataset.currentData);
    const zoneMarker = zoneMarkers.find(
      (zm) => zm.zone === zone.dataset.zone
    );
    if (zoneMarker) {
      zoneMarker.marker.setIcon({
        path: google.maps.SymbolPath.CIRCLE,
        scale: 12,
        fillColor: data.color,
        fillOpacity: 0.8,
        strokeColor: '#ffffff',
        strokeWeight: 2,
      });
    }
  });
}

// ── Transport Suggestions ─────────────────────────────────────────────

async function loadTransportSuggestions() {
  const transportList = document.getElementById('transport-list');
  if (!transportList) return;

  try {
    // Local transport for Salt Lake Stadium, Kolkata
    const transports = [
      { type: '\ud83d\ude87', name: 'Salt Lake Sector V Metro', time: '8 min walk', status: 'On time' },
      { type: '\ud83d\ude8c', name: 'Bus Route 215 (Salt Lake)', time: '5 min walk', status: 'On time' },
      { type: '\ud83d\ude97', name: 'Parking Block A & B', time: '6 min walk', status: '60% full' },
      { type: '\ud83d\ude95', name: 'Rideshare Drop-off (Gate 5)', time: '2 min walk', status: 'Available' },
    ];

    transportList.innerHTML = transports
      .map(
        (t) => `
        <div class="flex items-center justify-between p-2 bg-surface-800/50 rounded-lg">
            <div class="flex items-center gap-2">
                <span>${t.type}</span>
                <span class="font-medium">${t.name}</span>
            </div>
            <div class="text-right">
                <div>${t.time}</div>
                <div class="text-xs ${t.status.includes('Delayed') || t.status.includes('full') ? 'text-neon-orange' : 'text-neon-green'}">${t.status}</div>
            </div>
        </div>`
      )
      .join('');
  } catch (err) {
    transportList.innerHTML =
      '<p class="text-surface-200/40">Unable to load transport data</p>';
  }
}
