function updateClock() {
    const clock = document.getElementById('clock-taskbar');
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    clock.textContent = `${hours}:${minutes}`;
  }
  
  setInterval(updateClock, 1000);
  updateClock();
  