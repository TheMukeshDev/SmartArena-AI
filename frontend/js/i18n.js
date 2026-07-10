const translations = {
  en: {
    "nav.features": "Features",
    "nav.stats": "Stats",
    "nav.tech": "Technology",
    "nav.login": "Login",
    "nav.dashboard": "Dashboard",
    "hero.badge": "FIFA World Cup 2026™ AI Intelligence",
    "hero.title1": "Smarter Stadiums.",
    "hero.title2": "Powered by AI.",
    "hero.subtitle": "Real-time crowd intelligence, predictive incident management, and sustainability tracking for the FIFA World Cup 2026™ — all from one intelligent command center.",
    "dash.welcome": "Welcome to your",
    "dash.subtitle": "Here's a real-time overview of the stadium.",
    "dash.admin.title": "Admin Operations",
    "dash.volunteer.title": "Volunteer Tasks",
    "dash.fan.title": "Fan Experience",
    "dash.logout": "Logout",
    "dash.chat.placeholder": "Ask something..."
  },
  es: {
    "nav.features": "Características",
    "nav.stats": "Estadísticas",
    "nav.tech": "Tecnología",
    "nav.login": "Acceso",
    "nav.dashboard": "Panel",
    "hero.badge": "Inteligencia AI - Copa Mundial de la FIFA 2026™",
    "hero.title1": "Estadios Inteligentes.",
    "hero.title2": "Impulsados por IA.",
    "hero.subtitle": "Inteligencia de multitudes en tiempo real, gestión predictiva de incidentes y seguimiento de sostenibilidad para la Copa Mundial de la FIFA 2026™: todo desde un centro de mando inteligente.",
    "dash.welcome": "Bienvenido a su",
    "dash.subtitle": "Aquí hay una visión general en tiempo real del estadio.",
    "dash.admin.title": "Operaciones de Administración",
    "dash.volunteer.title": "Tareas de Voluntarios",
    "dash.fan.title": "Experiencia del Aficionado",
    "dash.logout": "Cerrar sesión",
    "dash.chat.placeholder": "Pregunta algo..."
  },
  fr: {
    "nav.features": "Fonctionnalités",
    "nav.stats": "Statistiques",
    "nav.tech": "Technologie",
    "nav.login": "Connexion",
    "nav.dashboard": "Tableau de bord",
    "hero.badge": "Intelligence IA - Coupe du Monde de la FIFA 2026™",
    "hero.title1": "Stades Intelligents.",
    "hero.title2": "Propulsés par l'IA.",
    "hero.subtitle": "Intelligence des foules en temps réel, gestion prédictive des incidents et suivi du développement durable pour la Coupe du Monde de la FIFA 2026™ - le tout depuis un centre de commande intelligent.",
    "dash.welcome": "Bienvenue sur votre",
    "dash.subtitle": "Voici un aperçu en temps réel du stade.",
    "dash.admin.title": "Opérations d'administration",
    "dash.volunteer.title": "Tâches des Bénévoles",
    "dash.fan.title": "Expérience des Fans",
    "dash.logout": "Déconnexion",
    "dash.chat.placeholder": "Demandez quelque chose..."
  },
  ar: {
    "nav.features": "الميزات",
    "nav.stats": "الإحصائيات",
    "nav.tech": "التكنولوجيا",
    "nav.login": "تسجيل الدخول",
    "nav.dashboard": "لوحة القيادة",
    "hero.badge": "ذكاء اصطناعي - كأس العالم لكرة القدم 2026™",
    "hero.title1": "ملاعب أذكى.",
    "hero.title2": "مدعومة بالذكاء الاصطناعي.",
    "hero.subtitle": "ذكاء الحشود في الوقت الفعلي، الإدارة التنبؤية للحوادث، وتتبع الاستدامة لكأس العالم 2026™ — كل ذلك من مركز قيادة ذكي واحد.",
    "dash.welcome": "مرحبًا بك في",
    "dash.subtitle": "إليك نظرة عامة في الوقت الفعلي على الملعب.",
    "dash.admin.title": "عمليات الإدارة",
    "dash.volunteer.title": "مهام المتطوعين",
    "dash.fan.title": "تجربة المشجعين",
    "dash.logout": "تسجيل خروج",
    "dash.chat.placeholder": "اسأل عن شيء..."
  },
  hi: {
    "nav.features": "विशेषताएं",
    "nav.stats": "आंकड़े",
    "nav.tech": "तकनीक",
    "nav.login": "लॉगिन",
    "nav.dashboard": "डैशबोर्ड",
    "hero.badge": "फीफा विश्व कप 2026™ एआई इंटेलिजेंस",
    "hero.title1": "स्मार्टर स्टेडियम।",
    "hero.title2": "एआई द्वारा संचालित।",
    "hero.subtitle": "रीयल-टाइम क्राउड इंटेलिजेंस, प्रेडिक्टिव इंसिडेंट मैनेजमेंट, और फीफा विश्व कप 2026™ के लिए सस्टेनेबिलिटी ट्रैकिंग — सब एक ही स्मार्ट कमांड सेंटर से।",
    "dash.welcome": "आपके",
    "dash.subtitle": "यहाँ स्टेडियम का रीयल-टाइम अवलोकन है।",
    "dash.admin.title": "व्यवस्थापक संचालन",
    "dash.volunteer.title": "स्वयंसेवक कार्य",
    "dash.fan.title": "प्रशंसक अनुभव",
    "dash.logout": "लॉग आउट",
    "dash.chat.placeholder": "कुछ पूछें..."
  }
};

function updateLanguage(lang) {
  localStorage.setItem('preferred_language', lang);
  
  if (lang === 'ar') {
    document.documentElement.dir = 'rtl';
    document.documentElement.lang = 'ar';
  } else {
    document.documentElement.dir = 'ltr';
    document.documentElement.lang = lang;
  }

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[lang] && translations[lang][key]) {
      if (el.tagName === 'INPUT' && el.type === 'text') {
        el.placeholder = translations[lang][key];
      } else {
        el.textContent = translations[lang][key];
      }
    }
  });
}

function getStoredLanguage() {
  return localStorage.getItem('preferred_language') || 'en';
}

document.addEventListener('DOMContentLoaded', () => {
  const currentLang = getStoredLanguage();
  
  // Setup language selector if it exists
  const langSelector = document.getElementById('lang-selector');
  if (langSelector) {
    langSelector.value = currentLang;
    langSelector.addEventListener('change', (e) => {
      updateLanguage(e.target.value);
    });
  }

  // Initial translation
  updateLanguage(currentLang);
});
