/**
 * SmartArena AI — Admin Panel Logic
 * ====================================
 *
 * Handles gate management, announcements, and security log pages.
 */

const Admin = (() => {
    const GATE_STATUSES = { open: 'bg-neon-green/20 text-neon-green', closed: 'bg-red-500/20 text-red-400', maintenance: 'bg-yellow-500/20 text-yellow-400' };

    async function authedFetch(path, opts = {}) {
        const defaults = { credentials: 'include', headers: { 'Content-Type': 'application/json' } };
        return fetch(CONFIG.apiUrl(path), { ...defaults, ...opts });
    }

    // ── Gates Page ────────────────────────────────────────────────────────
    async function initGatesPage() {
        const loading = document.getElementById('loading-state');
        const content = document.getElementById('gates-content');
        const modal = document.getElementById('gate-modal');
        const form = document.getElementById('gate-form');
        let gates = [];

        async function loadGates() {
            loading.classList.remove('hidden');
            content.classList.add('hidden');
            try {
                const res = await authedFetch('/admin/gates');
                const json = await res.json();
                gates = json.data?.gates || [];
                renderGates();
            } catch (e) {
                content.innerHTML = '<p class="text-red-400 text-center py-8">Failed to load gates.</p>';
                content.classList.remove('hidden');
            } finally {
                loading.classList.add('hidden');
            }
        }

        function renderGates() {
            if (!gates.length) {
                content.innerHTML = '<p class="text-surface-200/40 text-center py-8">No gates found.</p>';
                content.classList.remove('hidden');
                return;
            }
            content.innerHTML = gates.map((g, i) => `
                <div class="glass-card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4" role="listitem">
                    <div class="flex-1">
                        <div class="flex items-center gap-3 mb-2">
                            <h3 class="font-bold text-lg">${escapeHtml(String(g.name))}</h3>
                            <span class="text-xs px-2 py-0.5 rounded-full font-medium ${GATE_STATUSES[g.status] || GATE_STATUSES.open}">${escapeHtml(String(g.status))}</span>
                        </div>
                        <div class="flex items-center gap-6 text-sm text-surface-200/60">
                            <span>Capacity: <strong class="text-white">${escapeHtml(String(g.capacity))}</strong></span>
                            <span>Current: <strong class="text-white">${escapeHtml(String(g.current_count))}</strong></span>
                        </div>
                        <div class="w-full bg-surface-800 h-1.5 rounded-full mt-2 max-w-xs">
                            <div class="bg-arena-500 h-1.5 rounded-full transition-all duration-500" style="width: ${Math.min(100, (g.current_count / g.capacity) * 100)}%"></div>
                        </div>
                    </div>
                    <button data-gate-idx="${i}" class="gate-edit-btn bg-surface-700 hover:bg-surface-600 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors whitespace-nowrap">Edit Gate</button>
                </div>
            `).join('');
            content.classList.remove('hidden');

            content.querySelectorAll('.gate-edit-btn').forEach(btn => {
                btn.addEventListener('click', () => openModal(gates[parseInt(btn.dataset.gateIdx)]));
            });
        }

        function openModal(gate) {
            document.getElementById('modal-gate-name').textContent = gate.name;
            document.getElementById('gate-status').value = gate.status;
            document.getElementById('gate-capacity').value = gate.capacity;
            modal.dataset.gateName = gate.name;
            modal.classList.remove('hidden');
        }

        document.getElementById('modal-close-btn').addEventListener('click', () => modal.classList.add('hidden'));
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.add('hidden'); });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Saving...';
            try {
                await authedFetch('/admin/gates', {
                    method: 'POST',
                    body: JSON.stringify({
                        name: modal.dataset.gateName,
                        status: document.getElementById('gate-status').value,
                        capacity: parseInt(document.getElementById('gate-capacity').value) || 5000,
                    }),
                });
                modal.classList.add('hidden');
                await loadGates();
            } catch (err) {
                showToast('Failed to update gate.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Save Changes';
            }
        });

        await loadGates();
    }

    // ── Announcements Page ────────────────────────────────────────────────
    async function initAnnouncementsPage() {
        const form = document.getElementById('announcement-form');
        const list = document.getElementById('ann-list');

        async function loadAnnouncements() {
            try {
                const res = await authedFetch('/admin/announcements');
                const json = await res.json();
                const items = json.data?.announcements || [];
                if (!items.length) {
                    list.innerHTML = '<p class="text-surface-200/40 text-sm text-center py-8">No announcements yet.</p>';
                    return;
                }
                list.innerHTML = items.map(a => `
                    <div class="bg-surface-800 p-4 rounded-xl border ${a.priority === 'urgent' ? 'border-red-500/30' : 'border-white/5'}">
                        <div class="flex items-center justify-between mb-1">
                            <h3 class="font-medium text-white">${escapeHtml(a.title)}</h3>
                            <div class="flex items-center gap-2">
                                <span class="text-xs px-2 py-0.5 rounded ${a.priority === 'urgent' ? 'bg-red-500/20 text-red-400' : 'bg-surface-700 text-surface-200'}">${a.priority}</span>
                                <button data-ann-id="${a.id}" class="ann-delete-btn text-surface-200/40 hover:text-red-400 text-lg" aria-label="Delete announcement">&times;</button>
                            </div>
                        </div>
                        <p class="text-sm text-surface-200/70 mb-2">${escapeHtml(a.message)}</p>
                        <div class="flex items-center gap-3 text-xs text-surface-200/40">
                            <span>${a.target_zones?.length ? escapeHtml(a.target_zones.join(', ')) : 'All Zones'}</span>
                            <span>${a.created_at ? new Date(a.created_at).toLocaleString() : ''}</span>
                        </div>
                    </div>
                `).join('');

                list.querySelectorAll('.ann-delete-btn').forEach(btn => {
                    btn.addEventListener('click', async () => {
                        if (!confirm('Delete this announcement?')) return;
                        await authedFetch(`/admin/announcements/${btn.dataset.annId}`, { method: 'DELETE' });
                        await loadAnnouncements();
                    });
                });
            } catch (e) {
                list.innerHTML = '<p class="text-red-400 text-sm text-center py-8">Failed to load announcements.</p>';
            }
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById('ann-submit');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Broadcasting...';
            try {
                const zones = document.getElementById('ann-zones').value;
                await authedFetch('/admin/announcements', {
                    method: 'POST',
                    body: JSON.stringify({
                        title: document.getElementById('ann-title').value,
                        message: document.getElementById('ann-message').value,
                        priority: document.getElementById('ann-priority').value,
                        target_zones: zones ? [zones] : [],
                    }),
                });
                form.reset();
                await loadAnnouncements();
            } catch (err) {
                showToast('Failed to broadcast announcement.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Broadcast Announcement';
            }
        });

        await loadAnnouncements();
    }

    // ── Security Logs Page ────────────────────────────────────────────────
    async function initSecurityLogsPage() {
        const loading = document.getElementById('loading-state');
        const content = document.getElementById('logs-content');
        const tbody = document.getElementById('logs-table-body');
        const empty = document.getElementById('logs-empty');

        async function loadLogs() {
            loading.classList.remove('hidden');
            content.classList.add('hidden');
            try {
                const res = await authedFetch('/admin/security/logs');
                const json = await res.json();
                const logs = json.data?.logs || [];
                if (!logs.length) {
                    tbody.innerHTML = '';
                    empty.classList.remove('hidden');
                } else {
                    empty.classList.add('hidden');
                    tbody.innerHTML = logs.map(l => `
                        <tr class="hover:bg-surface-800/50 transition-colors">
                            <td class="px-4 py-3 text-surface-200/60 whitespace-nowrap">${l.timestamp ? new Date(l.timestamp).toLocaleString() : '-'}</td>
                            <td class="px-4 py-3 whitespace-nowrap"><span class="text-xs px-2 py-0.5 rounded bg-surface-800 text-arena-400 font-mono">${escapeHtml(l.event_type || '-')}</span></td>
                            <td class="px-4 py-3 text-surface-200/80">${escapeHtml(l.description || '-')}</td>
                            <td class="px-4 py-3 text-surface-200/40 font-mono text-xs">${escapeHtml(l.admin_uid || '-')}</td>
                        </tr>
                    `).join('');
                }
                content.classList.remove('hidden');
            } catch (e) {
                content.innerHTML = '<p class="text-red-400 text-center py-8">Failed to load security logs.</p>';
                content.classList.remove('hidden');
            } finally {
                loading.classList.add('hidden');
            }
        }

        document.getElementById('refresh-logs-btn').addEventListener('click', loadLogs);
        await loadLogs();
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    return { initGatesPage, initAnnouncementsPage, initSecurityLogsPage };
})();
