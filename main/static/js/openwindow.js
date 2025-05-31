const categoryBtn = document.querySelector('.open-category-window');
  const categoryWindow = document.getElementById('categoryWindow');

  categoryBtn.addEventListener('click', () => {
    categoryWindow.style.display = 'block';
  });

  function closeCategoryWindow() {
    categoryWindow.style.display = 'none';
  }

  window.addEventListener('click', function (e) {
    if (e.target === categoryWindow) {
      categoryWindow.style.display = 'none';
    }
  });