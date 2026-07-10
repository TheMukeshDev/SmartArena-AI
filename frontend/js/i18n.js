/**
 * SmartArena AI — Internationalization (i18n)
 * ==============================================
 *
 * FIFA World Cup 2026: supports English, Spanish, French, Arabic.
 */

const I18N = {
  _locale: "en",
  _listeners: [],

  translations: {
    en: {
      "app.name": "SmartArena AI",
      "nav.dashboard": "Dashboard",
      "nav.map": "Live Map",
      "nav.eco": "Eco Dashboard",
      "nav.logout": "Logout",
      "map.title": "Live Heatmap",
      "map.subtitle": "Real-time crowd occupancy tracking",
      "map.legend.low": "Low",
      "map.legend.med": "Med",
      "map.legend.high": "High",
      "map.legend.max": "Max",
      "map.legend.label": "Crowd Level",
      "map.analyze": "Run AI Crowd Analysis",
      "map.analyzing": "Analyzing...",
      "map.zone.details": "Zone Details",
      "map.zone.empty": "Click a stadium zone on the map to view live analytics.",
      "map.zone.occupancy": "Occupancy",
      "map.zone.headcount": "Headcount",
      "map.zone.capacity": "Capacity Limit",
      "map.zone.insights": "AI Insights",
      "panel.status.optimal": "Optimal",
      "panel.status.moderate": "Moderate",
      "panel.status.congested": "Congested",
      "panel.status.critical": "Critical",
      "ai.global.strategy": "AI Global Strategy",
      "dashboard.welcome": "Welcome to your Dashboard",
      "dashboard.subtitle": "Here's a real-time overview of the stadium.",
      "dashboard.occupancy": "Current Occupancy",
      "dashboard.incidents": "Active Incidents",
      "dashboard.energy": "Energy Usage",
      "dashboard.optimized": "Optimized",
      "dashboard.incident.reporter": "AI Incident Reporter",
      "dashboard.incident.desc": "Describe the incident (AI will classify and prioritize it)",
      "dashboard.incident.submit": "Report to AI",
      "dashboard.eco.title": "Sustainability Hub",
      "dashboard.eco.optimize": "Run AI Eco-Optimizer",
      "dashboard.admin": "Admin Controls",
      "dashboard.volunteer": "Volunteer Tasks",
      "dashboard.fan": "Fan Experience",
      "auth.login.title": "Welcome Back",
      "auth.login.subtitle": "Sign in to access your stadium dashboard",
      "auth.login.email": "Email",
      "auth.login.password": "Password",
      "auth.login.forgot": "Forgot Password?",
      "auth.login.submit": "Sign In",
      "auth.login.google": "Continue with Google",
      "auth.login.noaccount": "Don't have an account?",
      "auth.login.signup": "Sign up",
      "auth.signup.title": "Create an Account",
      "auth.signup.subtitle": "Join the intelligent stadium network",
      "auth.signup.name": "Full Name",
      "auth.signup.email": "Email",
      "auth.signup.password": "Password",
      "auth.signup.role": "Role",
      "auth.signup.submit": "Create Account",
      "auth.signup.hasaccount": "Already have an account?",
      "auth.signup.signin": "Sign in",
      "auth.reset.title": "Reset Password",
      "auth.reset.subtitle": "Enter your email and we'll send you a link to reset your password.",
      "auth.reset.submit": "Send Reset Link",
      "auth.reset.back": "Back to Login",
      "common.loading": "Loading...",
      "common.error": "Error",
      "language.label": "Language",
      "language.en": "English",
      "language.es": "Español",
      "language.fr": "Français",
      "language.ar": "العربية",
    },
    es: {
      "app.name": "SmartArena AI",
      "nav.dashboard": "Panel",
      "nav.map": "Mapa",
      "nav.eco": "Eco Panel",
      "nav.logout": "Cerrar sesión",
      "map.title": "Mapa de Calor",
      "map.subtitle": "Seguimiento de ocupación en tiempo real",
      "map.legend.low": "Bajo",
      "map.legend.med": "Med",
      "map.legend.high": "Alto",
      "map.legend.max": "Máx",
      "map.legend.label": "Nivel de Multitud",
      "map.analyze": "Analizar con IA",
      "map.analyzing": "Analizando...",
      "map.zone.details": "Detalles de Zona",
      "map.zone.empty": "Haga clic en una zona del estadio para ver análisis.",
      "map.zone.occupancy": "Ocupación",
      "map.zone.headcount": "Personas",
      "map.zone.capacity": "Capacidad",
      "map.zone.insights": "Análisis IA",
      "panel.status.optimal": "Óptimo",
      "panel.status.moderate": "Moderado",
      "panel.status.congested": "Congestionado",
      "panel.status.critical": "Crítico",
      "ai.global.strategy": "Estrategia Global IA",
      "dashboard.welcome": "Bienvenido a tu Panel",
      "dashboard.subtitle": "Vista general del estadio en tiempo real.",
      "dashboard.occupancy": "Ocupación Actual",
      "dashboard.incidents": "Incidentes Activos",
      "dashboard.energy": "Uso de Energía",
      "dashboard.optimized": "Optimizado",
      "dashboard.incident.reporter": "Reporte de Incidentes IA",
      "dashboard.incident.desc": "Describa el incidente (la IA lo clasificará)",
      "dashboard.incident.submit": "Reportar a IA",
      "dashboard.eco.title": "Centro de Sostenibilidad",
      "dashboard.eco.optimize": "Ejecutar Eco-Optimizador IA",
      "dashboard.admin": "Controles de Admin",
      "dashboard.volunteer": "Tareas de Voluntario",
      "dashboard.fan": "Experiencia del Fan",
      "auth.login.title": "Bienvenido",
      "auth.login.subtitle": "Inicia sesión para acceder al panel",
      "auth.login.email": "Correo",
      "auth.login.password": "Contraseña",
      "auth.login.forgot": "¿Olvidaste tu contraseña?",
      "auth.login.submit": "Iniciar sesión",
      "auth.login.google": "Continuar con Google",
      "auth.login.noaccount": "¿No tienes cuenta?",
      "auth.login.signup": "Regístrate",
      "auth.signup.title": "Crear una Cuenta",
      "auth.signup.subtitle": "Únete a la red inteligente del estadio",
      "auth.signup.name": "Nombre Completo",
      "auth.signup.email": "Correo",
      "auth.signup.password": "Contraseña",
      "auth.signup.role": "Rol",
      "auth.signup.submit": "Crear Cuenta",
      "auth.signup.hasaccount": "¿Ya tienes cuenta?",
      "auth.signup.signin": "Inicia sesión",
      "auth.reset.title": "Restablecer Contraseña",
      "auth.reset.subtitle": "Ingresa tu correo para recibir un enlace de restablecimiento.",
      "auth.reset.submit": "Enviar Enlace",
      "auth.reset.back": "Volver a Inicio",
      "common.loading": "Cargando...",
      "common.error": "Error",
      "language.label": "Idioma",
      "language.en": "English",
      "language.es": "Español",
      "language.fr": "Français",
      "language.ar": "العربية",
    },
    fr: {
      "app.name": "SmartArena AI",
      "nav.dashboard": "Tableau",
      "nav.map": "Carte",
      "nav.eco": "Éco Tableau",
      "nav.logout": "Déconnexion",
      "map.title": "Carte Thermique",
      "map.subtitle": "Suivi d'occupation en temps réel",
      "map.legend.low": "Faible",
      "map.legend.med": "Moy",
      "map.legend.high": "Élevé",
      "map.legend.max": "Max",
      "map.legend.label": "Niveau de Foule",
      "map.analyze": "Analyser avec IA",
      "map.analyzing": "Analyse en cours...",
      "map.zone.details": "Détails de la Zone",
      "map.zone.empty": "Cliquez sur une zone du stade pour voir les analyses.",
      "map.zone.occupancy": "Occupation",
      "map.zone.headcount": "Effectif",
      "map.zone.capacity": "Capacité",
      "map.zone.insights": "Analyses IA",
      "panel.status.optimal": "Optimal",
      "panel.status.moderate": "Modéré",
      "panel.status.congested": "Congestionné",
      "panel.status.critical": "Critique",
      "ai.global.strategy": "Stratégie Globale IA",
      "dashboard.welcome": "Bienvenue sur votre Tableau",
      "dashboard.subtitle": "Aperçu en temps réel du stade.",
      "dashboard.occupancy": "Occupation Actuelle",
      "dashboard.incidents": "Incidents Actifs",
      "dashboard.energy": "Consommation Énergie",
      "dashboard.optimized": "Optimisé",
      "dashboard.incident.reporter": "Signaleur d'Incidents IA",
      "dashboard.incident.desc": "Décrivez l'incident (l'IA le classera)",
      "dashboard.incident.submit": "Signaler à l'IA",
      "dashboard.eco.title": "Centre de Durabilité",
      "dashboard.eco.optimize": "Exécuter Éco-Optimiseur IA",
      "dashboard.admin": "Contrôles Admin",
      "dashboard.volunteer": "Tâches Bénévole",
      "dashboard.fan": "Expérience Fan",
      "auth.login.title": "Bon Retour",
      "auth.login.subtitle": "Connectez-vous pour accéder au tableau",
      "auth.login.email": "Courriel",
      "auth.login.password": "Mot de passe",
      "auth.login.forgot": "Mot de passe oublié?",
      "auth.login.submit": "Se connecter",
      "auth.login.google": "Continuer avec Google",
      "auth.login.noaccount": "Pas de compte?",
      "auth.login.signup": "S'inscrire",
      "auth.signup.title": "Créer un Compte",
      "auth.signup.subtitle": "Rejoignez le réseau intelligent du stade",
      "auth.signup.name": "Nom Complet",
      "auth.signup.email": "Courriel",
      "auth.signup.password": "Mot de passe",
      "auth.signup.role": "Rôle",
      "auth.signup.submit": "Créer le Compte",
      "auth.signup.hasaccount": "Déjà un compte?",
      "auth.signup.signin": "Connectez-vous",
      "auth.reset.title": "Réinitialiser le Mot de Passe",
      "auth.reset.subtitle": "Entrez votre courriel pour recevoir un lien de réinitialisation.",
      "auth.reset.submit": "Envoyer le Lien",
      "auth.reset.back": "Retour à la Connexion",
      "common.loading": "Chargement...",
      "common.error": "Erreur",
      "language.label": "Langue",
      "language.en": "English",
      "language.es": "Español",
      "language.fr": "Français",
      "language.ar": "العربية",
    },
    ar: {
      "app.name": "SmartArena AI",
      "nav.dashboard": "لوحة القيادة",
      "nav.map": "الخريطة",
      "nav.eco": "لوحة البيئة",
      "nav.logout": "تسجيل الخروج",
      "map.title": "خريطة الحرارة",
      "map.subtitle": "تتبع الإشغال في الوقت الفعلي",
      "map.legend.low": "منخفض",
      "map.legend.med": "متوسط",
      "map.legend.high": "مرتفع",
      "map.legend.max": "أقصى",
      "map.legend.label": "مستوى الحشود",
      "map.analyze": "تحليل بالذكاء الاصطناعي",
      "map.analyzing": "جارٍ التحليل...",
      "map.zone.details": "تفاصيل المنطقة",
      "map.zone.empty": "انقر على منطقة في الملعب لعرض التحليلات.",
      "map.zone.occupancy": "الإشغال",
      "map.zone.headcount": "عدد الأفراد",
      "map.zone.capacity": "الحد الأقصى",
      "map.zone.insights": "تحليلات الذكاء الاصطناعي",
      "panel.status.optimal": "مثالي",
      "panel.status.moderate": "معتدل",
      "panel.status.congested": "مزدحم",
      "panel.status.critical": "خطير",
      "ai.global.strategy": "الاستراتيجية العامة للذكاء الاصطناعي",
      "dashboard.welcome": "مرحباً بك في لوحة القيادة",
      "dashboard.subtitle": "نظرة عامة على الملعب في الوقت الفعلي.",
      "dashboard.occupancy": "الإشغال الحالي",
      "dashboard.incidents": "الحوادث النشطة",
      "dashboard.energy": "استهلاك الطاقة",
      "dashboard.optimized": "محسّن",
      "dashboard.incident.reporter": "مبلغ الحوادث بالذكاء الاصطناعي",
      "dashboard.incident.desc": "صف الحادث (سيقوم الذكاء الاصطناعي بتصنيفه)",
      "dashboard.incident.submit": "الإبلاغ للذكاء الاصطناعي",
      "dashboard.eco.title": "مركز الاستدامة",
      "dashboard.eco.optimize": "تشغيل المحسّن البيئي بالذكاء الاصطناعي",
      "dashboard.admin": "عناصر تحكم المشرف",
      "dashboard.volunteer": "مهام المتطوع",
      "dashboard.fan": "تجربة المشجع",
      "auth.login.title": "مرحباً بعودتك",
      "auth.login.subtitle": "سجل الدخول للوصول إلى لوحة القيادة",
      "auth.login.email": "البريد الإلكتروني",
      "auth.login.password": "كلمة المرور",
      "auth.login.forgot": "هل نسيت كلمة المرور؟",
      "auth.login.submit": "تسجيل الدخول",
      "auth.login.google": "المتابعة مع Google",
      "auth.login.noaccount": "ليس لديك حساب؟",
      "auth.login.signup": "اشتراك",
      "auth.signup.title": "إنشاء حساب",
      "auth.signup.subtitle": "انضم إلى الشبكة الذكية للملعب",
      "auth.signup.name": "الاسم الكامل",
      "auth.signup.email": "البريد الإلكتروني",
      "auth.signup.password": "كلمة المرور",
      "auth.signup.role": "الدور",
      "auth.signup.submit": "إنشاء حساب",
      "auth.signup.hasaccount": "هل لديك حساب بالفعل؟",
      "auth.signup.signin": "تسجيل الدخول",
      "auth.reset.title": "إعادة تعيين كلمة المرور",
      "auth.reset.subtitle": "أدخل بريدك الإلكتروني لاستلام رابط إعادة التعيين.",
      "auth.reset.submit": "إرسال الرابط",
      "auth.reset.back": "العودة إلى تسجيل الدخول",
      "common.loading": "جارٍ التحميل...",
      "common.error": "خطأ",
      "language.label": "اللغة",
      "language.en": "English",
      "language.es": "Español",
      "language.fr": "Français",
      "language.ar": "العربية",
    },
  },

  get locale() {
    return this._locale;
  },

  set locale(code) {
    if (this.translations[code]) {
      this._locale = code;
      document.documentElement.lang = code;
      if (code === "ar") {
        document.documentElement.dir = "rtl";
      } else {
        document.documentElement.dir = "ltr";
      }
      localStorage.setItem("smartarena_locale", code);
      this._notify();
    }
  },

  onLocaleChanged(fn) {
    this._listeners.push(fn);
  },

  _notify() {
    this._listeners.forEach((fn) => fn(this._locale));
  },

  t(key, ...args) {
    const tr = this.translations[this._locale] || this.translations.en;
    let val = tr[key] || this.translations.en[key] || key;
    if (args.length) {
      args.forEach((arg, i) => {
        val = val.replace(`{${i}}`, arg);
      });
    }
    return val;
  },

  init() {
    const saved = localStorage.getItem("smartarena_locale");
    const browserLang = navigator.language?.split("-")[0];
    const supported = ["en", "es", "fr", "ar"];
    const preferred = saved || (supported.includes(browserLang) ? browserLang : "en");
    this.locale = preferred;
  },

  renderLanguageSwitcher(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const supported = [
      { code: "en", label: "English" },
      { code: "es", label: "Español" },
      { code: "fr", label: "Français" },
      { code: "ar", label: "العربية" },
    ];
    container.innerHTML = supported
      .map(
        (lang) =>
          `<button class="lang-btn text-xs px-2 py-1 rounded transition-colors ${
            this._locale === lang.code
              ? "bg-arena-500 text-white"
              : "text-surface-200 hover:text-white"
          }" data-lang="${lang.code}" aria-label="${lang.label}">${lang.label}</button>`
      )
      .join(" ");
    container.querySelectorAll(".lang-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        this.locale = btn.dataset.lang;
        this.renderLanguageSwitcher(containerId);
        this._notify();
      });
    });
  },
};

document.addEventListener("DOMContentLoaded", () => I18N.init());
