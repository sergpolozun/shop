document.addEventListener("DOMContentLoaded", () => {
    const startButton = document.getElementById("startButton");
    const startMenu = document.getElementById("startMenu");
  
    startButton.addEventListener("click", () => {
      startMenu.style.display = startMenu.style.display === "block" ? "none" : "block";
    });
  
    document.addEventListener("click", (e) => {
      if (!startMenu.contains(e.target) && e.target !== startButton) {
        startMenu.style.display = "none";
      }
    });
  });
  
  // Закрывает все окна с классом win95-window
  function closeAllWindows() {
    const windows = document.querySelectorAll(".win95-window");
    windows.forEach(win => {
      win.style.display = "none";
    });
    document.getElementById("startMenu").style.display = "none";
  }
  