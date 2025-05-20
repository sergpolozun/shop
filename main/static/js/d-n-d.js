function makeDraggable(elem) {
    let posX = 0, posY = 0, mouseX = 0, mouseY = 0;
  
    elem.onmousedown = dragMouseDown;
  
    function dragMouseDown(e) {
      e = e || window.event;
      e.preventDefault();
      // стартовые координаты мыши
      mouseX = e.clientX;
      mouseY = e.clientY;
      document.onmouseup = closeDragElement;
      document.onmousemove = elementDrag;
    }
  
    function elementDrag(e) {
      e = e || window.event;
      e.preventDefault();
      // считаем разницу движения мыши
      posX = mouseX - e.clientX;
      posY = mouseY - e.clientY;
      mouseX = e.clientX;
      mouseY = e.clientY;
      // меняем позицию элемента
      elem.style.top = (elem.offsetTop - posY) + "px";
      elem.style.left = (elem.offsetLeft - posX) + "px";
    }
  
    function closeDragElement() {
      document.onmouseup = null;
      document.onmousemove = null;
    }
  }
  
  // Применим к окнам и ярлыкам
  window.onload = () => {
    document.querySelectorAll('.win95-window, .icon').forEach(el => {
      el.style.position = 'absolute'; // для ярлыков
      makeDraggable(el);
    });
  };
  