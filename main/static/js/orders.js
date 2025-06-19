// JavaScript для модального окна заказов

function openOrdersModal() {
    const modal = document.getElementById('ordersModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.style.alignItems = 'center';
        modal.style.justifyContent = 'center';
        
        // Фокус на кнопку "Понятно" для удобства
        const okBtn = modal.querySelector('button[onclick="closeOrdersModal()"]');
        if (okBtn) {
            okBtn.focus();
        }
    }
}

function closeOrdersModal() {
    const modal = document.getElementById('ordersModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Закрытие модального окна при клике вне его
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('ordersModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeOrdersModal();
            }
        });
    }
    
    // Закрытие по Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeOrdersModal();
        }
    });
}); 