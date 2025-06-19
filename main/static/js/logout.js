// JavaScript для модального окна подтверждения выхода

function openLogoutModal() {
    const modal = document.getElementById('logoutModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        
        // Фокус на кнопку "Отмена" для удобства
        const cancelBtn = modal.querySelector('button[onclick="closeLogoutModal()"]');
        if (cancelBtn) {
            cancelBtn.focus();
        }
    }
}

function closeLogoutModal() {
    const modal = document.getElementById('logoutModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Закрытие модального окна при клике вне его
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('logoutModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeLogoutModal();
            }
        });
    }
    
    // Закрытие по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeLogoutModal();
        }
    });
}); 