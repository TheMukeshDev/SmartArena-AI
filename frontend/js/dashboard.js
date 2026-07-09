document.addEventListener('DOMContentLoaded', async () => {
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
                incidentSubmit.textContent = 'AI Analyzing...';
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
                        aiPriority.textContent = c.priority + " Priority";
                        
                        // Set color based on priority
                        aiPriority.className = 'badge ' + (c.priority === 'High' || c.priority === 'Critical' ? 'badge-danger' : 'badge-warning');
                        
                        aiAction.textContent = c.action;
                        aiAnnouncement.textContent = c.announcement || "No announcement needed.";
                        aiResult.classList.remove('hidden');
                        document.getElementById('incident-desc').value = '';
                    } else {
                        alert("AI failed to process incident.");
                    }
                } catch (err) {
                    console.error(err);
                    alert("Error contacting AI service.");
                } finally {
                    incidentSubmit.disabled = false;
                    incidentSubmit.textContent = 'Report to AI';
                }
            });
        }

        // Volunteer Task Assignment Logic
        const reqTaskBtn = document.getElementById('req-task-btn');
        const volTaskList = document.getElementById('vol-task-list');
        
        if (reqTaskBtn) {
            reqTaskBtn.addEventListener('click', async () => {
                reqTaskBtn.disabled = true;
                reqTaskBtn.textContent = 'Thinking...';
                
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
                        const t = data.data;
                        
                        // Create new task element
                        const li = document.createElement('li');
                        li.className = 'flex flex-col p-4 bg-surface-800 rounded-lg border border-neon-blue/30 animate-pulse';
                        
                        const pClass = t.priority === 'High' || t.priority === 'Critical' 
                            ? 'bg-red-500/20 text-red-400' 
                            : 'bg-yellow-500/20 text-yellow-400';

                        li.innerHTML = `
                            <div class="flex items-center justify-between mb-1">
                                <span class="font-medium text-neon-blue">AI: ${t.task}</span>
                                <span class="text-xs ${pClass} px-2 py-1 rounded">${t.priority} Priority</span>
                            </div>
                            <p class="text-sm text-surface-200/80">${t.description}</p>
                        `;
                        
                        // Add to top of list
                        volTaskList.prepend(li);
                        
                        // Remove pulse after 2s
                        setTimeout(() => li.classList.remove('animate-pulse'), 2000);
                    }
                } catch (err) {
                    console.error(err);
                    alert("Failed to get task from AI.");
                } finally {
                    reqTaskBtn.disabled = false;
                    reqTaskBtn.textContent = 'Ask AI for Task';
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

            const appendMessage = (text, isUser = false) => {
                const div = document.createElement('div');
                div.className = isUser 
                    ? 'bg-arena-600 text-sm text-white p-3 rounded-xl rounded-tr-none self-end ml-auto w-10/12'
                    : 'bg-surface-800 text-sm text-surface-200 p-3 rounded-xl rounded-tl-none border border-white/5 self-start w-10/12';
                div.textContent = text;
                chatMessages.appendChild(div);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            };

            chatForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const query = chatInput.value.trim();
                if (!query) return;

                appendMessage(query, true);
                chatInput.value = '';
                
                // Show typing indicator
                const typingId = 'typing-' + Date.now();
                const typingDiv = document.createElement('div');
                typingDiv.id = typingId;
                typingDiv.className = 'text-xs text-surface-200 italic ml-2';
                typingDiv.textContent = 'ArenaBot is typing...';
                chatMessages.appendChild(typingDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;

                try {
                    const res = await fetch(CONFIG.apiUrl("/ai/assistant/chat"), {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ query: query }),
                        credentials: "include"
                    });
                    
                    document.getElementById(typingId).remove();
                    const data = await res.json();
                    
                    if (res.ok) {
                        appendMessage(data.data.reply);
                    } else {
                        appendMessage("Sorry, I encountered an error.");
                    }
                } catch (err) {
                    document.getElementById(typingId)?.remove();
                    appendMessage("Network error. Please try again.");
                }
            });
        }

    } catch (err) {
        console.error("Initialization failed:", err);
    }
});
