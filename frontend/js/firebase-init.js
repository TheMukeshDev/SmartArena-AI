/**
 * SmartArena AI — Firebase Client Configuration
 * ================================================
 *
 * Initializes Firebase client-side SDK for Authentication,
 * Firestore, and Analytics.
 *
 * Config values are defined in config.js (FIREBASE_CONFIG).
 * Firebase client config is public by design — security is
 * enforced by Firebase Security Rules and Auth, not by hiding config.
 */

let firebaseApp = null;
let firebaseAuth = null;
let firebaseDb = null;

/**
 * Initialize Firebase client SDK.
 * Uses inline config from config.js to eliminate the critical request
 * chain to the backend, improving page load performance.
 * @returns {Promise<object>} Firebase app instance
 */
async function initFirebase() {
  if (firebaseApp) return firebaseApp;

  try {
    const firebaseConfig = CONFIG.FIREBASE_CONFIG;

    // Initialize Firebase
    firebaseApp = firebase.initializeApp(firebaseConfig);
    firebaseAuth = firebase.auth();
    firebaseDb = firebase.firestore();

    console.debug("[SmartArena] Firebase initialized successfully");
    return firebaseApp;
  } catch (error) {
    console.error("[SmartArena] Firebase initialization failed:", error);
    throw error;
  }
}

/**
 * Get Firebase Auth instance.
 * @returns {object|null} Firebase Auth instance
 */
function getAuth() {
  return firebaseAuth;
}

/**
 * Get Firestore instance.
 * @returns {object|null} Firestore instance
 */
function getDb() {
  return firebaseDb;
}
