document.addEventListener("DOMContentLoaded", () => {
  const startButton = document.getElementById("startButton");
  const startMenu = document.getElementById("startMenu");
  const desktopButton = document.getElementById("desktopButton");

  startButton.addEventListener("click", () => {
      startMenu.style.display = startMenu.style.display === "block" ? "none" : "block";
  });

  document.addEventListener("click", (e) => {
      if (!startMenu.contains(e.target) && e.target !== startButton) {
          startMenu.style.display = "none";
      }
  });

  desktopButton.addEventListener("click", () => {
      const homeUrl = desktopButton.dataset.url;
      // Сначала закрываем окна
      closeAllWindows();
      // Потом переходим
      window.location.href = homeUrl;
  });
});

function closeAllWindows() {
  const windows = document.querySelectorAll(".win95-window");
  windows.forEach(win => {
      win.style.display = "none";
  });
  const menu = document.getElementById("startMenu");
  if (menu) menu.style.display = "none";
}
