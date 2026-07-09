/**
 * SmartArena AI — Main Application Logic
 * ========================================
 *
 * Handles page initialization, animations, and API health checks.
 */

document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

/**
 * Initialize the application.
 */
async function initApp() {
  animateHero();
  animateStats();
  animateFeatureCards();
  checkBackendHealth();
  initNavScroll();
  initMobileMenu();
}

// ── Animations ─────────────────────────────────────────────────────────

/**
 * Animate the hero section elements with staggered entrance.
 */
function animateHero() {
  const heroElements = document.querySelectorAll("[data-animate='hero']");
  heroElements.forEach((el, index) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(30px)";
    setTimeout(() => {
      el.style.transition = `opacity 0.8s ease, transform 0.8s ease`;
      el.style.opacity = "1";
      el.style.transform = "translateY(0)";
    }, 200 + index * 150);
  });
}

/**
 * Animate stat counters with counting effect.
 */
function animateStats() {
  const statElements = document.querySelectorAll("[data-count]");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.dataset.count, 10);
          animateCount(el, 0, target, 2000);
          observer.unobserve(el);
        }
      });
    },
    { threshold: 0.5 }
  );

  statElements.forEach((el) => observer.observe(el));
}

/**
 * Animate a number from start to end.
 * @param {HTMLElement} el - Target element
 * @param {number} start - Start value
 * @param {number} end - End value
 * @param {number} duration - Animation duration in ms
 */
function animateCount(el, start, end, duration) {
  const startTime = performance.now();
  const suffix = el.dataset.suffix || "";

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(start + (end - start) * eased);

    el.textContent = current.toLocaleString() + suffix;

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

/**
 * Animate feature cards on scroll.
 */
function animateFeatureCards() {
  const cards = document.querySelectorAll("[data-animate='card']");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate-slide-up");
          entry.target.style.opacity = "1";
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: "0px 0px -50px 0px" }
  );

  cards.forEach((card) => {
    card.style.opacity = "0";
    observer.observe(card);
  });
}

// ── Navigation ─────────────────────────────────────────────────────────

/**
 * Add scroll-based navbar styling.
 */
function initNavScroll() {
  const nav = document.getElementById("main-nav");
  if (!nav) return;

  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      nav.classList.add("bg-surface-950/90", "backdrop-blur-xl", "shadow-lg");
      nav.classList.remove("bg-transparent");
    } else {
      nav.classList.remove("bg-surface-950/90", "backdrop-blur-xl", "shadow-lg");
      nav.classList.add("bg-transparent");
    }
  });
}

/**
 * Initialize mobile hamburger menu toggle.
 */
function initMobileMenu() {
  const toggle = document.getElementById("mobile-menu-toggle");
  const menu = document.getElementById("mobile-menu");
  if (!toggle || !menu) return;

  toggle.addEventListener("click", () => {
    menu.classList.toggle("hidden");
    menu.classList.toggle("flex");
  });
}

// ── API Health Check ───────────────────────────────────────────────────

/**
 * Check backend API health and update status indicator.
 */
async function checkBackendHealth() {
  const indicator = document.getElementById("api-status");
  if (!indicator) return;

  try {
    const response = await fetch(CONFIG.baseUrl("/health"), {
      method: "GET",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(5000),
    });

    if (response.ok) {
      indicator.classList.add("bg-neon-green");
      indicator.classList.remove("bg-red-500", "bg-yellow-500");
      indicator.title = "Backend: Connected";
    } else {
      indicator.classList.add("bg-yellow-500");
      indicator.title = "Backend: Degraded";
    }
  } catch {
    indicator.classList.add("bg-red-500");
    indicator.title = "Backend: Offline";
  }
}
