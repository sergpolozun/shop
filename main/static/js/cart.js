// cart.js

function openProductModal(productId) {
  fetch(`/shop/product/${productId}/detail/`)
    .then(response => response.json())
    .then(data => {
      let modal = document.getElementById('productModal');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'productModal';
        modal.className = 'modal-win98';
        modal.innerHTML = `<div class="modal-content-win98">
          <div class="modal-header-win98">
            <h3 id="modalTitle">Детали товара</h3>
            <button class="close-btn-win98" onclick="closeProductModal()">×</button>
          </div>
          <div class="modal-body-win98" id="modalBody"></div>
        </div>`;
        document.body.appendChild(modal);
      }
      document.getElementById('modalTitle').textContent = data.name;
      document.getElementById('modalBody').innerHTML = data.html;
      modal.style.display = 'flex';
    });
}

function closeProductModal() {
  let modal = document.getElementById('productModal');
  if (modal) modal.style.display = 'none';
}

function changeQtyModal(btn, delta) {
  console.log('changeQtyModal called with delta:', delta);
  const form = btn.closest('form');
  const input = form.querySelector('input[name="quantity"]');
  let value = parseInt(input.value) || 1;
  value += delta;
  if (value < 1) value = 1;
  input.value = value;
  console.log('New quantity value:', value);
  
  // Автоматически обновляем количество в корзине
  const productId = form.action.split('/').slice(-2)[0]; // Извлекаем ID товара из URL формы
  console.log('Auto-updating cart for productId:', productId);
  
  const formData = new FormData(form);
  
  fetch(form.action, {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    }
  })
  .then(response => {
    console.log('Auto-update response status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Auto-update response data:', data);
    if (data.success) {
      showNotification('Количество обновлено', 'success');
    } else {
      showNotification('Ошибка при обновлении количества', 'error');
    }
  })
  .catch(error => {
    console.error('Auto-update error:', error);
    showNotification('Ошибка при обновлении количества', 'error');
  });
}

function addToCart(event, productId) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  
  fetch(form.action, {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Показываем уведомление об успешном добавлении
      showNotification(data.message, 'success');
      // Сбрасываем количество на 1
      const quantityInput = form.querySelector('input[name="quantity"]');
      quantityInput.value = 1;
    } else {
      showNotification('Ошибка при добавлении в корзину', 'error');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showNotification('Ошибка при добавлении в корзину', 'error');
  });
  
  return false;
}

function showNotification(message, type) {
  // Создаем уведомление
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  // Удаляем уведомление через 3 секунды
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, 3000);
}

function openPaymentModal() {
  document.getElementById('paymentModal').style.display = 'flex';
}

function closePaymentModal() {
  document.getElementById('paymentModal').style.display = 'none';
}

function openClearCartModal() {
  document.getElementById('clearCartModal').style.display = 'flex';
}

function closeClearCartModal() {
  document.getElementById('clearCartModal').style.display = 'none';
}

function changeQty(btn, delta) {
  const form = btn.closest('form');
  const input = form.querySelector('input[name="quantity"]');
  let value = parseInt(input.value) || 1;
  value += delta;
  if (value < 1) value = 1;
  input.value = value;
  form.submit();
}

function addToCartSimple(productId) {
  console.log('addToCartSimple called with productId:', productId);
  
  // Получаем CSRF-токен из модального окна или создаем его
  const modal = document.getElementById('productModal');
  let csrfToken = modal.querySelector('input[name="csrfmiddlewaretoken"]');
  
  if (!csrfToken) {
    console.log('CSRF token not found in modal, creating new one');
    // Если CSRF-токена нет, создаем его
    csrfToken = document.createElement('input');
    csrfToken.type = 'hidden';
    csrfToken.name = 'csrfmiddlewaretoken';
    csrfToken.value = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    modal.appendChild(csrfToken);
  }
  
  console.log('CSRF token:', csrfToken.value);
  
  const formData = new FormData();
  formData.append('quantity', '1');
  formData.append('csrfmiddlewaretoken', csrfToken.value);
  
  console.log('Sending request to:', `/shop/cart/add/${productId}/`);
  
  fetch(`/shop/cart/add/${productId}/`, {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    }
  })
  .then(response => {
    console.log('Response status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Response data:', data);
    if (data.success) {
      showNotification(data.message, 'success');
      // Обновляем модальное окно, чтобы показать форму с количеством
      setTimeout(() => {
        openProductModal(productId);
      }, 500);
    } else {
      showNotification('Ошибка при добавлении в корзину', 'error');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showNotification('Ошибка при добавлении в корзину', 'error');
  });
}

function updateCartQuantity(productId) {
  console.log('updateCartQuantity called with productId:', productId);
  
  const form = document.getElementById(`updateForm_${productId}`);
  console.log('Form:', form);
  
  if (!form) {
    console.error('Form not found for productId:', productId);
    showNotification('Ошибка: форма не найдена', 'error');
    return;
  }
  
  const formData = new FormData(form);
  
  // Логируем данные формы
  for (let [key, value] of formData.entries()) {
    console.log('Form data:', key, value);
  }
  
  console.log('Sending request to:', form.action);
  
  fetch(form.action, {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    }
  })
  .then(response => {
    console.log('Response status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Response data:', data);
    if (data.success) {
      showNotification('Количество обновлено', 'success');
    } else {
      showNotification('Ошибка при обновлении количества', 'error');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showNotification('Ошибка при обновлении количества', 'error');
  });
}

// --- JS для пересчёта суммы на лету ---
document.addEventListener('DOMContentLoaded', function() {
  // Обработчик для полей количества в корзине
  document.querySelectorAll('.cart-qty-input-win98').forEach(function(input) {
    input.addEventListener('input', function() {
      let value = parseInt(this.value) || 1;
      if (value < 1) value = 1;
      this.value = value;
      // Получить цену из data-атрибута
      const price = parseFloat(this.getAttribute('data-price'));
      // Пересчитать сумму
      const subtotal = price * value;
      const tr = this.closest('tr');
      const subtotalTd = tr.querySelector('.cart-item-subtotal');
      subtotalTd.textContent = subtotal.toLocaleString('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' ₽';
      subtotalTd.setAttribute('data-subtotal', subtotal);
      // Пересчитать итоговую сумму
      let total = 0;
      document.querySelectorAll('.cart-item-subtotal').forEach(function(td) {
        total += parseFloat(td.getAttribute('data-subtotal')) || 0;
      });
      const totalBlock = document.querySelector('.cart-total-win98 b');
      if (totalBlock) {
        totalBlock.textContent = 'Итого: ' + total.toLocaleString('ru-RU', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' ₽';
      }
    });
  });

  // Обработчик для полей количества в модальном окне товара
  let updateTimeout;
  document.addEventListener('input', function(event) {
    if (event.target.classList.contains('cart-qty-input-win98') && event.target.closest('#productModal')) {
      const input = event.target;
      let value = parseInt(input.value) || 1;
      if (value < 1) value = 1;
      input.value = value;
      
      // Очищаем предыдущий таймаут
      clearTimeout(updateTimeout);
      
      // Устанавливаем задержку для обновления
      updateTimeout = setTimeout(() => {
        // Автоматически обновляем количество в корзине
        const form = input.closest('form');
        if (form) {
          const productId = form.action.split('/').slice(-2)[0];
          console.log('Auto-updating cart for productId:', productId, 'with quantity:', value);
          
          const formData = new FormData(form);
          
          fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
              'X-Requested-With': 'XMLHttpRequest',
            }
          })
          .then(response => {
            console.log('Auto-update response status:', response.status);
            return response.json();
          })
          .then(data => {
            console.log('Auto-update response data:', data);
            if (data.success) {
              showNotification('Количество обновлено', 'success');
            } else {
              showNotification('Ошибка при обновлении количества', 'error');
            }
          })
          .catch(error => {
            console.error('Auto-update error:', error);
            showNotification('Ошибка при обновлении количества', 'error');
          });
        }
      }, 500); // Задержка 500мс
    }
  });

  window.onclick = function(event) {
    const paymentModal = document.getElementById('paymentModal');
    const clearCartModal = document.getElementById('clearCartModal');
    const productModal = document.getElementById('productModal');
    if (event.target === paymentModal) {
      closePaymentModal();
    }
    if (event.target === clearCartModal) {
      closeClearCartModal();
    }
    if (event.target === productModal) {
      closeProductModal();
    }
  }
}); 