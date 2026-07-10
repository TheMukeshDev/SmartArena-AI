document.addEventListener('DOMContentLoaded', async () => {
    function t(key) {
        return window.I18N ? window.I18N.t(key) : key;
    }

    const userNameEl = document.getElementById('user-name');
    const userRoleBadge = document.getElementById('user-role-badge');
    const logoutBtn = document.getElementById('logout-btn');
    const loadingState = document.getElementById('loading-state');
    const dashboardContent = document.getElementById('dashboard-content');
    
    // Panels
    const adminPanel = document.getElementById('admin-panel');
    const volunteerPanel = document.getElementById('volunteer-panel');
    const fanPanel = document.getElementById('fan-panel');

    try {
        await initFirebase();

        Auth.initAuthListener(async (user) => {
            if (!user) {
                window.location.href = 'login.html';
                return;
            }

            // Display user basic info
            userNameEl.textContent = user.displayName || user.email;

            try {
                // Fetch the session cookie profile from the backend to verify 
                // full auth works and to get the role securely
                const res = await fetch(CONFIG.apiUrl("/auth/me"), {
                    method: "GET",
                    credentials: "include"
                });
                
                if (!res.ok) throw new Error("Failed to fetch backend profile");
                const profile = await res.json();
                const role = profile.data?.role || 'fan';

                // Show role badge
                userRoleBadge.textContent = role;
                userRoleBadge.classList.remove('hidden');
                
                // Show Role-specific content
                if (role === 'admin') adminPanel.classList.remove('hidden');
                if (role === 'volunteer') volunteerPanel.classList.remove('hidden');
                if (role === 'fan') fanPanel.classList.remove('hidden');

                // Show Dashboard
                loadingState.classList.add('hidden');
                dashboardContent.classList.remove('hidden');

            } catch (err) {
                console.error("Backend auth failed:", err);
                // If backend rejects the session (or it's missing), logout to reset state
                Auth.logout();
            }
        });

        logoutBtn.addEventListener('click', () => {
            Auth.logout();
        });

        // Incident Reporting Logic
        const incidentForm = document.getElementById('incident-form');
        const incidentSubmit = document.getElementById('incident-submit');
        const aiResult = document.getElementById('ai-incident-result');
        const aiCategory = document.getElementById('ai-category');
        const aiPriority = document.getElementById('ai-priority');
        const aiAction = document.getElementById('ai-action');
        const aiAnnouncement = document.getElementById('ai-announcement');

        if (incidentForm) {
            incidentForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                incidentSubmit.disabled = true;
                incidentSubmit.textContent = t('dash.incident.analyzing');
                aiResult.classList.add('hidden');

                const desc = document.getElementById('incident-desc').value;

                try {
                    const res = await fetch(CONFIG.apiUrl("/ai/incident"), {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ description: desc }),
                        credentials: "include"
                    });
                    
                    const data = await res.json();
                    if (res.ok) {
                        const c = data.data.classification;
                        aiCategory.textContent = c.category;
                        aiPriority.textContent = c.priority + t('dash.priority.suffix');
                        
                        // Set color based on priority
                        aiPriority.className = 'badge ' + (c.priority === 'High' || c.priority === 'Critical' ? 'badge-danger' : 'badge-warning');
                        
                        aiAction.textContent = c.action;
                        aiAnnouncement.textContent = c.announcement || t('dash.incident.no_announcement');
                        aiResult.classList.remove('hidden');
                        document.getElementById('incident-desc').value = '';
                    } else {
                        alert(t('dash.incident.error'));
                    }
                } catch (err) {
                    console.error(err);
                    alert(t('dash.incident.network_error'));
                } finally {
                    incidentSubmit.disabled = false;
                    incidentSubmit.textContent = t('dash.incident.submit');
                }
            });
        }

        // Volunteer Task Assignment Logic
        const reqTaskBtn = document.getElementById('req-task-btn');
        const volTaskList = document.getElementById('vol-task-list');
        
        if (reqTaskBtn) {
            reqTaskBtn.addEventListener('click', async () => {
                reqTaskBtn.disabled = true;
                reqTaskBtn.textContent = t('vol.thinking');
                
                const loc = document.getElementById('vol-location').value;
                
                try {
                    const res = await fetch(CONFIG.apiUrl("/ai/volunteer/assign"), {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ location: loc }),
                        credentials: "include"
                    });
                    
                    const data = await res.json();
                    if (res.ok) {
                        const task = data.data;
                        
                        const li = document.createElement('li');
                        li.className = 'flex flex-col p-4 bg-surface-800 rounded-lg border border-neon-blue/30 animate-pulse';
                        
                        const pClass = task.priority === 'High' || task.priority === 'Critical' 
                            ? 'bg-red-500/20 text-red-400' 
                            : 'bg-yellow-500/20 text-yellow-400';

                        const header = document.createElement('div');
                        header.className = 'flex items-center justify-between mb-1';

                        const taskLabel = document.createElement('span');
                        taskLabel.className = 'font-medium text-neon-blue';
                        taskLabel.textContent = t('dash.volunteer.ai_prefix') + task.task;

                        const priorityBadge = document.createElement('span');
                        priorityBadge.className = 'text-xs ' + pClass + ' px-2 py-1 rounded';
                        priorityBadge.textContent = task.priority + t('dash.priority.suffix');

                        header.appendChild(taskLabel);
                        header.appendChild(priorityBadge);

                        const desc = document.createElement('p');
                        desc.className = 'text-sm text-surface-200/80';
                        desc.textContent = task.description;

                        li.appendChild(header);
                        li.appendChild(desc);
                        
                        volTaskList.prepend(li);
                        setTimeout(() => li.classList.remove('animate-pulse'), 2000);
                    }
                } catch (err) {
                    console.error(err);
                    alert(t('vol.error_task'));
                } finally {
                    reqTaskBtn.disabled = false;
                    reqTaskBtn.textContent = t('vol.ask');
                }
            });
        }

        // Fan Transport Suggestion Logic
        const fanPlanBtn = document.getElementById('fan-plan-btn');
        if (fanPlanBtn) {
            fanPlanBtn.addEventListener('click', async () => {
                const gate = document.getElementById('fan-gate').value || 'Gate C';
                const time = document.getElementById('fan-time').value || '18:00';
                
                fanPlanBtn.disabled = true;
                fanPlanBtn.textContent = t('dash.fan.planning');
                const resultDiv = document.getElementById('fan-route-result');
                const titleEl = document.getElementById('fan-route-title');

                try {
                    const res = await fetch(CONFIG.apiUrl("/ai/transport/suggest"), {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ gate: gate, arrival_time: time }),
                        credentials: "include"
                    });
                    const result = await res.json();
                    
                    if (res.ok && result.data) {
                        const data = result.data;
                        titleEl.textContent = data.recommended_mode + ' (~' + data.estimated_travel_time_minutes + 'm)';
                        
                        const dirP = document.createElement('p');
                        dirP.className = 'font-medium text-white mb-2';
                        dirP.textContent = data.directions;

                        const altP = document.createElement('p');
                        altP.className = 'text-xs';
                        const altStrong = document.createElement('strong');
                        altStrong.textContent = t('dash.fan.backup');
                        altP.appendChild(altStrong);
                        altP.appendChild(document.createTextNode(data.alternative));

                        resultDiv.replaceChildren(dirP, altP);
                    }
                } catch (err) {
                    console.error(err);
                    const errP = document.createElement('p');
                    errP.className = 'text-red-400';
                    errP.textContent = t('dash.fan.error');
                    resultDiv.replaceChildren(errP);
                } finally {
                    fanPlanBtn.disabled = false;
                    fanPlanBtn.textContent = t('dash.fan.route');
                }
            });
        }

        // Phase 9: AI Assistant Logic
        const chatToggle = document.getElementById('ai-chat-toggle');
        const chatWindow = document.getElementById('ai-chat-window');
        const chatClose = document.getElementById('ai-chat-close');
        const chatForm = document.getElementById('ai-chat-form');
        const chatInput = document.getElementById('ai-chat-input');
        const chatMessages = document.getElementById('ai-chat-messages');

        if (chatToggle) {
            const toggleChat = () => {
                const isHidden = chatWindow.classList.toggle('hidden');
                chatToggle.setAttribute('aria-expanded', !isHidden);
                if (!isHidden) {
                    chatInput.focus();
                }
            };
            chatToggle.addEventListener('click', toggleChat);
            chatClose.addEventListener('click', toggleChat);

            // Priority 3: Focus Trap for Accessibility
            chatWindow.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    const focusableElements = chatWindow.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                    const firstElement = focusableElements[0];
                    const lastElement = focusableElements[focusableElements.length - 1];

                    if (e.shiftKey) { // Shift + Tab
                        if (document.activeElement === firstElement) {
                            lastElement.focus();
                            e.preventDefault();
                        }
                    } else { // Tab
                        if (document.activeElement === lastElement) {
                            firstElement.focus();
                            e.preventDefault();
                        }
                    }
                } else if (e.key === 'Escape') {
                    chatWindow.classList.add('hidden');
                    chatToggle.setAttribute('aria-expanded', 'false');
                    chatToggle.focus();
                }
            });

            let isTtsEnabled = true;
            
            const speakText = (text) => {
                if (!isTtsEnabled || !('speechSynthesis' in window)) return;
                const utterance = new SpeechSynthesisUtterance(text);
                // Attempt to select a better voice
                const voices = window.speechSynthesis.getVoices();
                const langCode = window.localStorage.getItem('preferred_language') || 'en';
                utterance.voice = voices.find(v => v.lang.startsWith(langCode)) || null;
                window.speechSynthesis.speak(utterance);
            };

            const appendMessage = (text, isUser = false) => {
                const div = document.createElement('div');
                div.className = isUser 
                    ? 'bg-arena-600 text-sm text-white p-3 rounded-xl rounded-tr-none self-end ml-auto w-10/12'
                    : 'bg-surface-800 text-sm text-surface-200 p-3 rounded-xl rounded-tl-none border border-white/5 self-start w-10/12';
                div.textContent = text;
                chatMessages.appendChild(div);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                if (!isUser) {
                    speakText(text);
                }
            };

            let previousInteractionId = null;

            // --- Voice Integration ---
            const micBtn = document.getElementById('ai-chat-mic');
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            
            if (micBtn && SpeechRecognition) {
                const recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                const langMap = { 'en': 'en-US', 'es': 'es-ES', 'fr': 'fr-FR', 'ar': 'ar-SA', 'hi': 'hi-IN' };
                recognition.lang = langMap[window.localStorage.getItem('preferred_language') || 'en'];

                recognition.onstart = () => {
                    micBtn.classList.add('text-neon-pink', 'animate-pulse');
                    chatInput.placeholder = t('dash.chat.listening');
                };

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    chatInput.value = transcript;
                    // Automatically submit after listening
                    chatForm.dispatchEvent(new Event('submit'));
                };

                recognition.onerror = (event) => {
                    console.error('Speech recognition error', event.error);
                };

                recognition.onend = () => {
                    micBtn.classList.remove('text-neon-pink', 'animate-pulse');
                    chatInput.placeholder = t('dash.chat.placeholder');
                };

                micBtn.addEventListener('click', () => {
                    recognition.start();
                });
            } else if (micBtn) {
                micBtn.style.display = 'none'; // Hide if not supported
            }
            // ------------------------

            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const query = chatInput.value.trim();
                if (!query) return;

                appendMessage(query, true);
                chatInput.value = '';
                
                // Stop any current speaking when user sends a new message
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel();
                }
                
                // Show typing indicator
                const typingId = 'typing-' + Date.now();
                const typingDiv = document.createElement('div');
                typingDiv.id = typingId;
                typingDiv.className = 'text-xs text-surface-200 italic ml-2';
                typingDiv.textContent = t('dash.chat.typing');
                chatMessages.appendChild(typingDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;

                try {
                    const res = await fetch(CONFIG.apiUrl("/ai/assistant/chat"), {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ 
                            query: query, 
                            previous_interaction_id: previousInteractionId,
                            preferred_language: window.localStorage.getItem('preferred_language') || 'en'
                        }),
                        credentials: "include"
                    });
                    
                    document.getElementById(typingId).remove();
                    const data = await res.json();
                    
                    if (res.ok) {
                        appendMessage(data.data.reply);
                        if (data.data.interaction_id) {
                            previousInteractionId = data.data.interaction_id;
                        }
                    } else {
                        appendMessage(t('dash.chat.error'));
                    }
                } catch (err) {
                    document.getElementById(typingId)?.remove();
                    appendMessage(t('dash.chat.network_error'));
                }
            });
        }

    } catch (err) {
        console.error("Initialization failed:", err);
    }

    // Phase 11: SSE Incident Stream
    const toastContainer = document.getElementById('incident-toast-container');
    if (toastContainer) {
        const evtSource = new EventSource(CONFIG.apiUrl("/events/incidents"));
        evtSource.addEventListener("incident", (e) => {
            try {
                const data = JSON.parse(e.data);
                const inc = data.incident;
                const toast = document.createElement('div');
                toast.className = 'fixed top-4 right-4 z-[200] bg-surface-800 border border-neon-orange/50 rounded-xl p-4 shadow-2xl animate-slide-up max-w-sm';
                toast.setAttribute('role', 'alert');
                toast.setAttribute('aria-live', 'assertive');

                const toastInner = document.createElement('div');
                toastInner.className = 'flex items-start gap-3';

                const alertIcon = document.createElement('span');
                alertIcon.className = 'text-2xl';
                alertIcon.setAttribute('aria-hidden', 'true');
                alertIcon.textContent = '\u{1F6A8}';

                const content = document.createElement('div');
                content.className = 'flex-1';

                const meta = document.createElement('div');
                meta.className = 'flex items-center gap-2 mb-1';
                const prioritySpan = document.createElement('span');
                prioritySpan.className = 'text-xs font-mono text-neon-orange';
                prioritySpan.textContent = inc.classification?.priority || 'UNKNOWN';
                const categorySpan = document.createElement('span');
                categorySpan.className = 'text-xs text-surface-200/40';
                categorySpan.textContent = inc.classification?.category || 'General';
                meta.appendChild(prioritySpan);
                meta.appendChild(categorySpan);

                const descP = document.createElement('p');
                descP.className = 'text-sm text-white';
                descP.textContent = inc.description;

                const actionP = document.createElement('p');
                actionP.className = 'text-xs text-surface-200/40 mt-1';
                actionP.textContent = inc.classification?.action || '';

                content.appendChild(meta);
                content.appendChild(descP);
                content.appendChild(actionP);

                const dismissBtn = document.createElement('button');
                dismissBtn.className = 'text-surface-200/40 hover:text-white';
                dismissBtn.setAttribute('aria-label', 'Dismiss');
                dismissBtn.textContent = '\u00D7';
                dismissBtn.addEventListener('click', () => toast.remove());

                toastInner.appendChild(alertIcon);
                toastInner.appendChild(content);
                toastInner.appendChild(dismissBtn);
                toast.appendChild(toastInner);
                toastContainer.appendChild(toast);
                setTimeout(() => toast.remove(), 15000);
            } catch (err) {
                console.error("SSE parse error:", err);
            }
        });
        evtSource.onerror = () => console.warn("SSE connection lost, will retry...");
    }
});
