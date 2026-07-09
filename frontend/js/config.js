/**
 * SmartArena AI — Frontend Configuration
 * ========================================
 *
 * Central configuration for API endpoints and app settings.
 */

const CONFIG = {
  // API Base URL — auto-detects environment
  API_BASE_URL:
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
      ? "http://localhost:5000"
      : "", // Production: same-origin

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
