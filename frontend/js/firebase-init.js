/**
 * SmartArena AI — Firebase Client Configuration
 * ================================================
 *
 * Initializes Firebase client-side SDK for Authentication,
 * Firestore, and Analytics.
 *
 * Config values are loaded from the backend /api/v1/config/firebase
 * endpoint to avoid hardcoding in the frontend.
 */

let firebaseApp = null;
let firebaseAuth = null;
let firebaseDb = null;

/**
 * Initialize Firebase client SDK.
 * Fetches config from backend API to avoid hardcoding credentials.
 * @returns {Promise<object>} Firebase app instance
 */
async function initFirebase() {
  if (firebaseApp) return firebaseApp;

  try {
    // Fetch Firebase config from backend
    const response = await fetch(CONFIG.apiUrl("/config/firebase"), {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch Firebase config: ${response.status}`);
    }

    const result = await response.json();
    const firebaseConfig = result.data;

    // Initialize Firebase
    firebaseApp = firebase.initializeApp(firebaseConfig);
    firebaseAuth = firebase.auth();
    firebaseDb = firebase.firestore();

    console.log("[SmartArena] Firebase initialized successfully");
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
