// JavaScript для страниц авторизации

document.addEventListener('DOMContentLoaded', function() {
    // Фокус на первое поле ввода при загрузке страницы
    const firstInput = document.querySelector('.form-group-win98 input');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Обработка нажатия Enter для отправки формы
    const form = document.querySelector('.login-form-win98');
    if (form) {
        form.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        });
    }
    
    // Анимация кнопок при нажатии
    const buttons = document.querySelectorAll('.btn-win98');
    buttons.forEach(button => {
        button.addEventListener('mousedown', function() {
            this.style.border = '2px inset #000';
            this.style.transform = 'translateY(1px)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.border = '2px outset #fff';
            this.style.transform = 'translateY(0)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.border = '2px outset #fff';
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Очистка ошибок при вводе
    const inputs = document.querySelectorAll('.form-group-win98 input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const errorDiv = this.parentNode.querySelector('.field-error-win98');
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
            
            const generalError = document.querySelector('.login-error-win98');
            if (generalError) {
                generalError.style.display = 'none';
            }
        });
    });
}); 