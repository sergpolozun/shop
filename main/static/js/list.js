// list.js

// Функции для модального окна товара
function openProductModal(productId) {
    fetch(`/shop/product/${productId}/detail/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('productModalTitle').textContent = data.name;
            document.getElementById('productModalBody').innerHTML = data.html;

            const productModal = document.getElementById('productModal');
            productModal.style.display = 'block';

            const productContent = productModal.querySelector('.modal-content-win98');
            productContent.style.width = '500px';
            productContent.style.height = '420px';
            productContent.style.position = 'absolute';
            productContent.style.top = '50%';
            productContent.style.left = '50%';
            productContent.style.margin = '0';
            productContent.style.transform = 'translate(-110%, -50%)';
        })
        .catch(error => {
            console.error('Ошибка загрузки данных о товаре:', error);
            document.getElementById('productModalBody').innerHTML = '<p>Ошибка загрузки данных</p>';
            document.getElementById('productModal').style.display = 'block';
        });
}

function closeProductModal() {
    document.getElementById('productModal').style.display = 'none';
    closeReviewsModal(); // Закрываем и окно отзывов
}

// Функции для модального окна отзывов
function openReviewsModal(productId) {
    fetch(`/shop/reviews/${productId}/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('reviewsModalBody').innerHTML = data.html;
            
            const reviewsModal = document.getElementById('reviewsModal');
            reviewsModal.style.display = 'block';

            const reviewsContent = reviewsModal.querySelector('.modal-content-win98');
            reviewsContent.style.width = '500px';
            reviewsContent.style.height = '420px';
            reviewsContent.style.position = 'absolute';
            reviewsContent.style.top = '50%';
            reviewsContent.style.left = '50%';
            reviewsContent.style.margin = '0';
            reviewsContent.style.transform = 'translate(10%, -50%)';
        })
        .catch(error => console.error('Ошибка загрузки отзывов:', error));
}

function closeReviewsModal() {
    const reviewsModal = document.getElementById('reviewsModal');
    if (reviewsModal) {
        reviewsModal.style.display = 'none';
    }
}

// Функции для модального окна категорий
function openCategories() {
    document.getElementById('categoriesModal').style.display = 'flex';
    highlightCurrentCategory();
}

function closeCategories() {
    document.getElementById('categoriesModal').style.display = 'none';
}

function selectCategory(categoryId) {
    const url = new URL(window.location);
    if (categoryId === 'all') {
        url.searchParams.delete('category');
    } else {
        url.searchParams.set('category', categoryId);
    }
    window.location.href = url.toString();
}

function highlightCurrentCategory() {
    const currentCategory = window.currentCategory || '';
    const categoryItems = document.querySelectorAll('.category-item');
    categoryItems.forEach(item => {
        item.classList.remove('selected');
        if (item.dataset.category === currentCategory || 
            (currentCategory === '' && item.dataset.category === 'all')) {
            item.classList.add('selected');
        }
    });
}

// Функции для модального окна фильтрации
function openFilter() {
    document.getElementById('filterModal').style.display = 'flex';
}

function closeFilter() {
    document.getElementById('filterModal').style.display = 'none';
}

// Функции для модального окна поиска
function openSearch() {
    document.getElementById('searchModal').style.display = 'flex';
    // Фокусируемся на поле поиска
    setTimeout(() => {
        document.getElementById('searchQuery').focus();
    }, 100);
}

function closeSearch() {
    document.getElementById('searchModal').style.display = 'none';
}

function performSearch(event) {
    event.preventDefault();
    const searchQuery = document.getElementById('searchQuery').value.trim();
    const notFoundMsg = document.getElementById('searchNotFoundMsg');
    if (notFoundMsg) notFoundMsg.style.display = 'none';
    
    if (searchQuery) {
        // AJAX-запрос для проверки наличия товаров
        const url = new URL(window.location.origin + window.location.pathname);
        url.searchParams.set('search', searchQuery);
        fetch(url.toString() + '&ajax=1')
            .then(response => response.json())
            .then(data => {
                if (data.found) {
                    // Есть товары — переходим на страницу
                    window.location.href = url.toString();
                } else {
                    // Нет товаров — показываем сообщение
                    let msg = document.getElementById('searchNotFoundMsg');
                    if (!msg) {
                        msg = document.createElement('div');
                        msg.id = 'searchNotFoundMsg';
                        msg.className = 'search-not-found-msg';
                        msg.style.marginTop = '18px';
                        msg.style.color = '#800000';
                        msg.style.fontSize = '14px';
                        msg.style.fontWeight = 'bold';
                        msg.style.background = '#fff4f4';
                        msg.style.padding = '10px 16px';
                        msg.style.border = '2px solid #c0c0c0';
                        msg.style.borderRadius = '4px';
                        document.querySelector('.search-form-container').appendChild(msg);
                    }
                    msg.textContent = 'Товара с таким названием или описанием не найдено, попробуйте другой запрос.';
                    msg.style.display = 'block';
                }
            });
    }
}

// Экспорт функций поиска в глобальную область видимости
window.openSearch = openSearch;
window.closeSearch = closeSearch;
window.performSearch = performSearch;

// Обработчик формы фильтрации
document.addEventListener('DOMContentLoaded', function() {
    var filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const url = new URL(window.location);
            // Обновляем параметры сортировки
            url.searchParams.set('sort', formData.get('sort'));
            url.searchParams.set('order', formData.get('order'));
            // Обновляем параметры диапазона цен
            const minPrice = formData.get('min_price');
            const maxPrice = formData.get('max_price');
            if (minPrice && minPrice.trim() !== '') {
                url.searchParams.set('min_price', minPrice);
            } else {
                url.searchParams.delete('min_price');
            }
            if (maxPrice && maxPrice.trim() !== '') {
                url.searchParams.set('max_price', maxPrice);
            } else {
                url.searchParams.delete('max_price');
            }
            // Сохраняем текущую категорию
            if (window.currentCategory && window.currentCategory !== 'all' && window.currentCategory !== 'None') {
                url.searchParams.set('category', window.currentCategory);
            } else {
                url.searchParams.delete('category');
            }
            window.location.href = url.toString();
        });
    }
    // Сброс фильтра
    var resetBtn = document.querySelector('#filterForm button[type="button"]');
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            resetFilter();
        });
    }
    // Закрытие модальных окон при клике вне их
    window.onclick = function(event) {
        const productModal = document.getElementById('productModal');
        const categoriesModal = document.getElementById('categoriesModal');
        const filterModal = document.getElementById('filterModal');
        const searchModal = document.getElementById('searchModal');
        const reviewsModal = document.getElementById('reviewsModal');

        if (event.target === productModal) {
            closeProductModal();
        }
        if (event.target === categoriesModal) {
            closeCategories();
        }
        if (event.target === filterModal) {
            closeFilter();
        }
        if (event.target === searchModal) {
            closeSearch();
        }
        if (event.target === reviewsModal) {
            closeReviewsModal();
        }
    };
    // Для highlightCurrentCategory (чтобы работало после рендера)
    window.currentCategory = document.body.getAttribute('data-current-category') || '';
    highlightCurrentCategory();
});

function resetFilter() {
    document.querySelector('input[name="sort"][value="popularity"]').checked = true;
    document.querySelector('input[name="order"][value="desc"]').checked = true;
    document.getElementById('minPrice').value = '';
    document.getElementById('maxPrice').value = '';
}

// Функция для работы с избранным в модальном окне
function toggleFavoriteModal(productId, btn) {
    fetch(`/shop/favorite/toggle/${productId}/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'added') {
            btn.classList.add('favorite-active');
            btn.textContent = 'Удалить из избранного';
            // Обновляем карточку товара в списке
            updateProductCardFavorite(productId, true);
        } else {
            btn.classList.remove('favorite-active');
            btn.textContent = 'Добавить в избранное';
            // Обновляем карточку товара в списке
            updateProductCardFavorite(productId, false);
        }
    })
    .catch(error => {
        console.error('Ошибка при работе с избранным:', error);
    });
}

// Функция для обновления карточки товара в списке
function updateProductCardFavorite(productId, isFavorite) {
    const productCard = document.querySelector(`.product-card[onclick*="${productId}"]`);
    if (productCard) {
        if (isFavorite) {
            productCard.classList.add('favorite-product');
        } else {
            productCard.classList.remove('favorite-product');
        }
    }
}

// Функция для перехода на страницу с сохранением параметров фильтрации
function goToPage(pageNumber) {
    const url = new URL(window.location);
    url.searchParams.set('page', pageNumber);
    // Сохраняем все параметры фильтрации и поиска
    window.location.href = url.toString();
}

// Модальное окно редактирования товара (для администратора)
function openEditProductModal(productId) {
    fetch(`/shop/product/${productId}/edit/`, { credentials: 'include' })
        .then(response => response.text())
        .then(html => {
            let editModal = document.getElementById('editProductModal');
            if (!editModal) {
                editModal = document.createElement('div');
                editModal.id = 'editProductModal';
                editModal.className = 'modal-win98';
                document.body.appendChild(editModal);
            }
            editModal.innerHTML = `
                <div class="modal-content-win98" style="width:500px;height:420px;position:absolute;top:50%;left:50%;margin:0;transform:translate(10%, -50%);">
                    <div class="modal-header-win98">
                        <h3>Редактировать товар</h3>
                        <button class="close-btn-win98" onclick="closeEditProductModal()">×</button>
                    </div>
                    <div class="modal-body-win98" id="editProductModalBody">${html}</div>
                </div>
            `;
            editModal.style.display = 'block';

            // Сдвигаем окно карточки товара налево
            const productModal = document.getElementById('productModal');
            if (productModal) {
                const productContent = productModal.querySelector('.modal-content-win98');
                if (productContent) {
                    productContent.style.transform = 'translate(-110%, -50%)';
                }
            }
        })
        .catch(error => {
            alert('Ошибка загрузки формы редактирования');
        });
}

function closeEditProductModal() {
    const editModal = document.getElementById('editProductModal');
    if (editModal) {
        editModal.style.display = 'none';
    }
    // Возвращаем окно карточки товара в центр
    const productModal = document.getElementById('productModal');
    if (productModal) {
        const productContent = productModal.querySelector('.modal-content-win98');
        if (productContent) {
            productContent.style.transform = 'translate(-50%, -50%)';
        }
    }
}

// Для отправки формы редактирования товара (через AJAX)
function submitEditProductForm(event, productId) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    fetch(`/shop/product/${productId}/edit/`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Товар успешно обновлён!');
            closeEditProductModal();
            location.reload();
        } else {
            document.getElementById('editProductModalBody').innerHTML = data.html;
        }
    })
    .catch(() => alert('Ошибка сохранения товара'));
}

// Для удаления товара (через AJAX)
function deleteProduct(productId) {
    if (!confirm('Вы уверены, что хотите удалить этот товар?')) return;
    fetch(`/shop/product/${productId}/delete/`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'X-CSRFToken': getCSRFToken(), 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Товар удалён!');
            closeEditProductModal();
            location.reload();
        } else {
            alert('Ошибка удаления товара');
        }
    })
    .catch(() => alert('Ошибка удаления товара'));
}

function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return '';
} 