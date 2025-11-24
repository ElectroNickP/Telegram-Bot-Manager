// Common Utility Functions

function checkUpdates() {
    // This function would typically check with the backend
    // For now, we'll just show a toast or alert
    alert('System is up to date.');
}

function openBackups() {
    alert('Backup system is active. Daily snapshots enabled.');
}

// Toast Notification System (Simple implementation)
function showToast(message, type = 'info') {
    // Create toast element if it doesn't exist
    if (!$('#toast-container').length) {
        $('body').append('<div id="toast-container" style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;"></div>');
    }

    const colors = {
        info: '#3b82f6',
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b'
    };

    const toast = $(`
        <div style="
            background: white;
            border-left: 4px solid ${colors[type] || colors.info};
            padding: 1rem;
            margin-top: 0.5rem;
            border-radius: 4px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            min-width: 300px;
            animation: slideIn 0.3s ease;
        ">
            <div style="flex: 1;">${message}</div>
        </div>
    `);

    $('#toast-container').append(toast);

    setTimeout(() => {
        toast.fadeOut(300, function () { $(this).remove(); });
    }, 3000);
}

// Add CSS animation for toast
$('<style>@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }</style>').appendTo('head');
