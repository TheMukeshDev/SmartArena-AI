/**
 * SmartArena AI — Frontend Configuration
 * ========================================
 *
 * Central configuration for API endpoints and app settings.
 */

const CONFIG = {
  // API Base URL — auto-detects environment
  API_BASE_URL:
    window.location.hostname === "127.0.0.1"
      ? "http://127.0.0.1:5000"
      : window.location.hostname === "localhost"
      ? "http://localhost:5000"
      : "https://smartarena-ai.onrender.com", // Production Render URL

  // API Version
  API_VERSION: "v1",

  // App Info
  APP_NAME: "SmartArena AI",
  APP_VERSION: "1.0.0",

  /**
   * Build a full API URL for a given endpoint path.
   * @param {string} path - API endpoint path (e.g., "/health")
   * @returns {string} Full API URL
   */
  apiUrl(path) {
    const cleanPath = path.startsWith("/") ? path : `/${path}`;
    return `${this.API_BASE_URL}/api/${this.API_VERSION}${cleanPath}`;
  },

  /**
   * Build a URL for non-versioned endpoints (e.g., /health).
   * @param {string} path - Endpoint path
   * @returns {string} Full URL
   */
  baseUrl(path) {
    const cleanPath = path.startsWith("/") ? path : `/${path}`;
    return `${this.API_BASE_URL}${cleanPath}`;
  },
};

// Freeze config to prevent mutations
Object.freeze(CONFIG);

// ── Global CSRF Injection ──────────────────────────────────────────────
let _csrfToken = null;
const _originalFetch = window.fetch;

window.fetch = async function (resource, options) {
  if (
    options && 
    ['POST', 'PUT', 'DELETE'].includes(options.method?.toUpperCase()) && 
    typeof resource === 'string' && 
    (resource.includes(CONFIG.API_BASE_URL) || resource.startsWith('/'))
  ) {
    if (!_csrfToken) {
      try {
        const tokenRes = await _originalFetch(CONFIG.baseUrl('/api/v1/csrf-token'), { credentials: 'include' });
        if (tokenRes.ok) {
          const data = await tokenRes.json();
          _csrfToken = data.csrf_token;
        }
      } catch (e) {
        console.warn('Failed to fetch CSRF token');
      }
    }
    
    if (_csrfToken) {
      options.headers = {
        ...options.headers,
        'X-CSRFToken': _csrfToken
      };
    }
  }
  return _originalFetch(resource, options);
};
