/**
 * SmartArena AI — Toast Notification Utility
 * =============================================
 *
 * Replaces browser alert() calls with accessible, styled toast notifications.
 * Uses role="alert" and aria-live="assertive" for screen reader compatibility.
 */

/* eslint-disable no-unused-vars */

function showToast(message, type = 'error') {
    let container = document.getElementById('incident-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'incident-toast-container';
        container.setAttribute('role', 'log');
        container.setAttribute('aria-live', 'polite');
        container.setAttribute('aria-label', 'Notifications');
        document.body.appendChild(container);
    }

    const colors = {
        error: 'border-red-500/50',
        success: 'border-neon-green/50',
        info: 'border-neon-blue/50',
        warning: 'border-yellow-500/50',
    };

    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-[200] bg-surface-800 border ${colors[type] || colors.error} rounded-xl p-4 shadow-2xl max-w-sm`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');

    const inner = document.createElement('div');
    inner.className = 'flex items-start gap-3';

    const icon = document.createElement('span');
    icon.className = 'text-xl';
    icon.setAttribute('aria-hidden', 'true');
    const icons = { error: '\u274C', success: '\u2705', info: '\u2139\uFE0F', warning: '\u26A0\uFE0F' };
    icon.textContent = icons[type] || icons.error;

    const text = document.createElement('p');
    text.className = 'text-sm text-white flex-1';
    text.textContent = message;

    const dismissBtn = document.createElement('button');
    dismissBtn.className = 'text-surface-200/40 hover:text-white';
    dismissBtn.setAttribute('aria-label', 'Dismiss');
    dismissBtn.textContent = '\u00D7';
    dismissBtn.addEventListener('click', () => toast.remove());

    inner.appendChild(icon);
    inner.appendChild(text);
    inner.appendChild(dismissBtn);
    toast.appendChild(inner);
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}
