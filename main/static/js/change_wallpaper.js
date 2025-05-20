const wallpapers = [
    '/static/wallpapers/wallpaper1.jpg',
    '/static/wallpapers/wallpaper2.jpg',
    '/static/wallpapers/wallpaper3.jpg',
    '/static/wallpapers/wallpaper4.jpg'
  ];
  
  let currentWallpaper = 0;
  let showingFirst = true;
  
  const layer1 = document.querySelector('.wallpaper1');
  const layer2 = document.querySelector('.wallpaper2');
  
  layer1.style.backgroundImage = `url('${wallpapers[0]}')`;
  layer1.classList.add('visible');
  
  document.getElementById('changeWallpaperBtn').addEventListener('click', () => {
    currentWallpaper = (currentWallpaper + 1) % wallpapers.length;
    const nextImage = `url('${wallpapers[currentWallpaper]}')`;
  
    if (showingFirst) {
      layer2.style.backgroundImage = nextImage;
      layer2.classList.add('visible');
      layer1.classList.remove('visible');
    } else {
      layer1.style.backgroundImage = nextImage;
      layer1.classList.add('visible');
      layer2.classList.remove('visible');
    }
  
    showingFirst = !showingFirst;
  });
  