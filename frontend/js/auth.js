/**
 * SmartArena AI — Authentication Logic
 * =====================================
 *
 * Handles Firebase Auth (Email/Google) and session exchange with the backend.
 */

const Auth = {
  // Current user state
  user: null,

  /**
   * Listen to Firebase Auth state changes.
   */
  initAuthListener(onStateChangeCallback) {
    const auth = getAuth();
    if (!auth) {
      console.error("[Auth] Firebase not initialized");
      return;
    }

    auth.onAuthStateChanged(async (user) => {
      this.user = user;
      
      if (user) {
        console.log("[Auth] User is signed in:", user.email);
        // Ensure session cookie exists
        await this.createBackendSession(user);
      } else {
        console.log("[Auth] User is signed out.");
      }

      if (typeof onStateChangeCallback === "function") {
        onStateChangeCallback(user);
      }
    });
  },

  /**
   * Log in with Email and Password
   */
  async loginWithEmail(email, password) {
    try {
      const auth = getAuth();
      const userCredential = await auth.signInWithEmailAndPassword(email, password);
      return userCredential.user;
    } catch (error) {
      console.error("[Auth] Login error:", error.message);
      throw error;
    }
  },

  /**
   * Sign up with Email, Password, and Role
   */
  async signup(name, email, password, role) {
    try {
      const auth = getAuth();
      const userCredential = await auth.createUserWithEmailAndPassword(email, password);
      const user = userCredential.user;

      // Update user profile with name
      await user.updateProfile({ displayName: name });

      // Register user role with backend
      await this.registerUserWithBackend(user.uid, email, name, role);

      // Force token refresh to get custom claims (role)
      await user.getIdToken(true);

      return user;
    } catch (error) {
      console.error("[Auth] Signup error:", error.message);
      throw error;
    }
  },

  /**
   * Log in with Google
   */
  async loginWithGoogle() {
    try {
      const auth = getAuth();
      const provider = new firebase.auth.GoogleAuthProvider();
      const userCredential = await auth.signInWithPopup(provider);
      const user = userCredential.user;

      // Check if new user (needs role registration) - defaulting to 'fan'
      if (userCredential.additionalUserInfo?.isNewUser) {
        await this.registerUserWithBackend(user.uid, user.email, user.displayName, 'fan');
        await user.getIdToken(true);
      }

      return user;
    } catch (error) {
      console.error("[Auth] Google Login error:", error.message);
      throw error;
    }
  },

  /**
   * Reset Password
   */
  async resetPassword(email) {
    try {
      const auth = getAuth();
      await auth.sendPasswordResetEmail(email);
      return true;
    } catch (error) {
      console.error("[Auth] Password reset error:", error.message);
      throw error;
    }
  },

  /**
   * Log out
   */
  async logout() {
    try {
      const auth = getAuth();
      await auth.signOut();
      
      // Clear backend session
      await fetch(CONFIG.apiUrl("/auth/sessionLogout"), {
        method: "POST"
      });
      
      this.user = null;
      // Redirect to login or home
      window.location.href = "/pages/login.html";
    } catch (error) {
      console.error("[Auth] Logout error:", error.message);
      throw error;
    }
  },

  /**
   * Exchange Firebase ID token for a backend session cookie
   */
  async createBackendSession(user) {
    try {
      const idToken = await user.getIdToken();
      
      const response = await fetch(CONFIG.apiUrl("/auth/sessionLogin"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // CSRF token would go here if implemented via header
        },
        body: JSON.stringify({ idToken })
      });

      if (!response.ok) {
        throw new Error("Failed to create backend session");
      }
      console.log("[Auth] Backend session created successfully.");
    } catch (error) {
      console.error("[Auth] Session creation error:", error);
    }
  },

  /**
   * Register user details in the backend (sets Firestore & custom claims)
   */
  async registerUserWithBackend(uid, email, name, role) {
    try {
      const response = await fetch(CONFIG.apiUrl("/auth/register"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uid, email, name, role })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.message || "Failed to register user details");
      }
    } catch (error) {
      console.error("[Auth] Registration error:", error);
      throw error;
    }
  }
};
