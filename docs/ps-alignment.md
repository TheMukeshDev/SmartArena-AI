# PS4 Alignment — FIFA World Cup 2026 Challenge 4: Smart Stadiums & Tournament Operations

This document maps every PS4 pillar to the specific feature, file, and route that implements it.

## Primary Demo Flow: Volunteer Co-Pilot

The system is designed around **one persona** (under-trained stadium volunteer) and **one vertical** (crowd management + multilingual coordination). Every feature feeds into the volunteer's real-time awareness.

**Volunteer Co-Pilot Page** (`frontend/pages/volunteer-copilot.html`):
- Shows live zone status grid with 8 stadium zones
- Displays AI-generated `recommended_action` in the volunteer's selected language (EN/ES/FR/AR/HI)
- "What should I do right now?" primary action card
- Global stadium status with 15-minute predictions
- Weather feed with operational notes
- Quick links to Live Map and Volunteer Hub

**Multilingual Crowd Intelligence** (`backend/app/config/prompts.py` → `CROWD_PROMPT`):
- `recommended_action` is now returned as a dict keyed by language code (`{"en": "...", "es": "...", "fr": "...", "ar": "...", "hi": "..."}`)
- Frontend renders the action in the user's UI language
- Test coverage: `test_crowd_analysis_returns_multilingual_action` and `test_crowd_analysis_fallback_has_multilingual_keys`

**Data Upload Hook** (`POST /api/v1/admin/import-dataset`):
- Admin-gated endpoint accepting CSV or JSON files
- Validates and imports zone occupancy, gate status, or incident log records
- Stored in Firestore under `imported_datasets` collection
- Frontend: drag-and-drop upload UI on admin gates page
- Test coverage: 6 tests covering JSON, CSV, validation, and RBAC

## Pillar Mapping

| Pillar | Feature | File(s) | Route(s) | Why |
|--------|---------|---------|----------|-----|
| **Navigation** | BFS shortest-path routing + accessible path variant | `backend/app/services/navigation.py` | `GET /api/v1/ai/navigation/path`, `GET /api/v1/ai/navigation/path/accessible`, `GET /api/v1/ai/navigation/zones` | Lets fans and volunteers find the fastest route between any two zones; accessible variant only uses ramped/accessible edges (no stairs) |
| **Crowd Management** | AI crowd density analysis with multilingual recommended actions + predictive 15-min forecasting | `backend/app/services/ai_service.py`, `backend/app/ai/gemini.py`, `backend/app/config/prompts.py` | `POST /api/v1/ai/crowd/analyze` | Gemini analyzes zone occupancy + trend history + weather to output current status, predicted_status_15min per zone, and a multilingual recommended_action dict — lets volunteers act before congestion happens |
| **Volunteer Co-Pilot** | Real-time volunteer guidance page with AI-recommended actions in volunteer's language | `frontend/pages/volunteer-copilot.html`, `frontend/pages/dashboard.html` | `POST /api/v1/ai/crowd/analyze`, `GET /api/v1/ai/weather` | Primary demo page — under-trained volunteer sees what to do right now, in their language, with zone predictions and routing advice |
| **Accessibility** | Wheelchair-accessible path routing + sensory-friendly zone flag | `backend/app/services/navigation.py` | `GET /api/v1/ai/navigation/path/accessible` | `find_accessible_path()` only traverses edges marked accessible; `SENSORY_FRIENDLY_ZONES` surfaced in zone API and AI Assistant |
| **Transportation** | AI transport advisor with weather-aware recommendations | `backend/app/services/ai_service.py`, `backend/app/ai/gemini.py`, `backend/app/services/weather.py` | `POST /api/v1/ai/transport/suggest`, `GET /api/v1/ai/weather` | Gemini recommends parking/transit/rideshare/walking based on gate, arrival time, and real-time weather |
| **Sustainability** | AI sustainability optimizer fed live weather context | `backend/app/services/ai_service.py`, `backend/app/ai/gemini.py`, `backend/app/services/weather.py` | `POST /api/v1/ai/sustainability/optimize` | Weather context injected into prompt so recommendations account for external conditions |
| **Multilingual Assistance** | ArenaBot AI Assistant + volunteer co-pilot page with 5-language UI + multilingual crowd analysis | `backend/app/services/ai_service.py`, `backend/app/ai/gemini.py`, `frontend/js/i18n.js`, `frontend/pages/volunteer-copilot.html` | `POST /api/v1/ai/assistant/chat`, `POST /api/v1/ai/crowd/analyze` | User sends `preferred_language: "hi"` → ArenaBot responds in Hindi; crowd analysis returns `recommended_action` dict keyed by language code; volunteer-copilot page renders in user's selected language |
| **Operational Intelligence** | Real-time SSE incident stream + predictive crowd forecasting + weather-aware ops notes | `backend/app/routes/events.py`, `backend/app/services/ai_service.py`, `backend/app/services/weather.py` | `GET /api/v1/events/incidents` (SSE), `POST /api/v1/ai/incident` | New incidents pushed in real-time via SSE; weather module generates `operational_note` |
| **Data Import** | Admin dataset upload (CSV/JSON) for zone, gate, and incident data | `backend/app/routes/admin.py`, `frontend/pages/admin-gates.html`, `frontend/js/admin.js` | `POST /api/v1/admin/import-dataset` | Admin can upload synthetic stadium data to populate the system — CSV or JSON with zone occupancy, gate status, and incident logs |
| **Real-time Decision Support** | Predictive crowd status + SSE live incident toasts + weather-driven recommendations | `backend/app/routes/events.py`, `backend/app/ai/gemini.py`, `frontend/js/map.js`, `frontend/js/dashboard.js` | `POST /api/v1/ai/crowd/analyze`, `GET /api/v1/events/incidents`, `GET /api/v1/ai/weather` | Three-tier: (1) crowd analysis returns predictions, (2) incidents stream as toasts, (3) weather data gives operators actionable context |

## Additional Supporting Features

| Feature | File(s) | PS4 Relevance |
|---------|---------|---------------|
| Offline-first PWA (Service Worker + Manifest) | `frontend/js/sw.js`, `frontend/manifest.json`, `frontend/js/app.js` | Ensures stadium map and AI Assistant remain viewable in venue dead zones |
| Weather widget with operational note | `backend/app/services/weather.py`, `GET /api/v1/ai/weather` | Feeds every weather-aware prompt and surfaces operational notes |
| Incident auto-push via SSE | `backend/app/routes/events.py`, `frontend/js/dashboard.js` | Eliminates manual refresh — organizers see incidents as toasts instantly |
| Sensory-friendly zone surfaces | `backend/app/services/navigation.py`, `frontend` map info panel | "Quiet space near Gate B" queries answered via `SENSORY_FRIENDLY_ZONES` |
| Prompt injection defense | `backend/app/ai/gemini.py` (`PROMPT_INJECTION_PATTERNS`, `sanitize_user_input`) | User text is sanitized before being inserted into Gemini prompts |
| Rate limiting (SQLite) | `backend/app/middleware/ratelimit.py` | Fixed-window per-IP rate limiting prevents abuse |
