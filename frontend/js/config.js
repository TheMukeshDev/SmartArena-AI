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

  // Firebase Client Config (public by design — used by Firebase JS SDK)
  FIREBASE_CONFIG: {
    apiKey: "AIzaSyBs9C08RY28LxkTAwYCraMEDqGNOeFnykM",
    authDomain: "smartarena-ai-eaa94.firebaseapp.com",
    projectId: "smartarena-ai-eaa94",
    storageBucket: "smartarena-ai-eaa94.firebasestorage.app",
    messagingSenderId: "568517956898",
    appId: "1:568517956898:web:ae14a05e7b07177f89417b",
    measurementId: "G-J63FCNYD3E",
  },

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

// ── Global Fetch Interceptor ──────────────────────────────────────────────
let _csrfToken = null;
let _csrfFetchPromise = null;
const _originalFetch = window.fetch;

window.fetch = async function (resource, options) {
  options = options || {};

  if (
    typeof resource === 'string' &&
    (resource.includes(CONFIG.API_BASE_URL) || resource.startsWith('/'))
  ) {
    // Skip interceptor for auth session endpoints — they are the auth entry
    // point and must not have Bearer/CSRF headers attached (sessionLogin
    // reads idToken from the body; sessionLogout needs no auth).
    const isAuthEndpoint = /\/auth\/(sessionLogin|sessionLogout)(\?|$)/.test(resource);
    if (isAuthEndpoint) {
      return _originalFetch(resource, options);
    }

    // 1. Attach Firebase Auth Bearer Token
    if (window.firebase && window.firebase.auth) {
      const currentUser = window.firebase.auth().currentUser;
      if (currentUser) {
        try {
          const idToken = await currentUser.getIdToken();
          options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${idToken}`
          };
        } catch (e) {
          console.warn('[Fetch Interceptor] Failed to get Firebase ID token:', e);
        }
      }
    }

    // 2. Attach CSRF Token for mutating requests
    if (['POST', 'PUT', 'DELETE'].includes(options.method?.toUpperCase())) {
      if (!_csrfToken) {
        if (!_csrfFetchPromise) {
          _csrfFetchPromise = (async () => {
            try {
              const tokenRes = await _originalFetch(CONFIG.baseUrl('/api/v1/csrf-token'), { credentials: 'include' });
              if (tokenRes.ok) {
                const data = await tokenRes.json();
                _csrfToken = data.csrf_token;
              }
            } catch (e) {
              console.warn('[Fetch Interceptor] Failed to fetch CSRF token');
            } finally {
              _csrfFetchPromise = null;
            }
          })();
        }
        await _csrfFetchPromise;
      }
      
      if (_csrfToken) {
        options.headers = {
          ...options.headers,
          'X-CSRFToken': _csrfToken
        };
      }
    }
  }
  
  return _originalFetch(resource, options);
};
