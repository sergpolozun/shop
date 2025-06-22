class PixelArtEditor {
    constructor() {
        this.canvas = document.getElementById('paint-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.isDrawing = false;
        this.currentTool = 'pencil';
        this.currentColor = '#000000';
        this.pixelSize = 8; // 512 / 64 = 8 пикселей на ячейку
        this.gridSize = 64; // 64x64 сетка
        
        // История для отмены действий
        this.history = [];
        this.historyIndex = -1;
        this.maxHistory = 50; // Максимальное количество действий в истории
        
        // Защита от слишком частого использования заливки
        this.lastFillTime = 0;
        this.fillCooldown = 100; // 100ms между заливками
        
        this.init();
    }
    
    init() {
        this.setupCanvas();
        this.setupEventListeners();
        this.setupTools();
        this.setupColorPalette();
        this.drawGrid();
        this.saveToHistory(); // Сохраняем начальное состояние
    }
    
    setupCanvas() {
        // Устанавливаем размер холста для пиксель-арт
        this.canvas.width = this.gridSize * this.pixelSize;
        this.canvas.height = this.gridSize * this.pixelSize;
        
        // Заполняем белым цветом
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    setupEventListeners() {
        // События мыши
        this.canvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.canvas.addEventListener('mousemove', (e) => this.draw(e));
        this.canvas.addEventListener('mouseup', () => this.stopDrawing());
        this.canvas.addEventListener('mouseleave', () => this.stopDrawing());
        
        // События касания для мобильных устройств
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startDrawing(e.touches[0]);
        });
        this.canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            this.draw(e.touches[0]);
        });
        this.canvas.addEventListener('touchend', () => this.stopDrawing());
        
        // Горячие клавиши
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'z') {
                    e.preventDefault();
                    this.undo();
                }
            }
        });
    }
    
    setupTools() {
        const tools = ['pencil-tool', 'eraser-tool', 'fill-tool'];
        
        tools.forEach(toolId => {
            const tool = document.getElementById(toolId);
            if (tool) {
                tool.addEventListener('click', () => this.selectTool(toolId));
            }
        });
        
        // Кнопка очистки
        const clearBtn = document.getElementById('clear-canvas');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearCanvas());
        }
        
        // Кнопка отмены
        const undoBtn = document.getElementById('undo-action');
        if (undoBtn) {
            undoBtn.addEventListener('click', () => this.undo());
        }
        
        // Кнопка скачивания
        const downloadBtn = document.getElementById('download-image');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadImage());
        }
    }
    
    setupColorPalette() {
        const colorSwatches = document.querySelectorAll('.color-swatch');
        
        colorSwatches.forEach(swatch => {
            swatch.addEventListener('click', () => {
                // Убираем активный класс у всех цветов
                colorSwatches.forEach(s => s.classList.remove('active'));
                // Добавляем активный класс к выбранному цвету
                swatch.classList.add('active');
                this.currentColor = swatch.dataset.color;
            });
        });
    }
    
    selectTool(toolId) {
        // Убираем активный класс у всех инструментов
        const tools = document.querySelectorAll('.tool-btn');
        tools.forEach(tool => tool.classList.remove('active'));
        
        // Добавляем активный класс к выбранному инструменту
        const selectedTool = document.getElementById(toolId);
        if (selectedTool) {
            selectedTool.classList.add('active');
        }
        
        // Устанавливаем текущий инструмент
        this.currentTool = toolId.replace('-tool', '');
    }
    
    getPixelCoordinates(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Преобразуем координаты в координаты сетки
        const gridX = Math.floor(x / this.pixelSize);
        const gridY = Math.floor(y / this.pixelSize);
        
        return { gridX, gridY, x, y };
    }
    
    startDrawing(e) {
        this.isDrawing = true;
        this.draw(e);
    }
    
    draw(e) {
        if (!this.isDrawing) return;
        
        const coords = this.getPixelCoordinates(e);
        const { gridX, gridY } = coords;
        
        // Проверяем границы
        if (gridX < 0 || gridX >= this.gridSize || gridY < 0 || gridY >= this.gridSize) {
            return;
        }
        
        switch (this.currentTool) {
            case 'pencil':
                this.drawPixel(gridX, gridY, this.currentColor);
                break;
            case 'eraser':
                this.drawPixel(gridX, gridY, '#ffffff');
                break;
            case 'fill':
                // Защита от слишком частого использования заливки
                const now = Date.now();
                if (now - this.lastFillTime > this.fillCooldown) {
                    this.lastFillTime = now;
                    this.floodFill(gridX, gridY, this.currentColor);
                }
                break;
        }
    }
    
    stopDrawing() {
        if (this.isDrawing) {
            this.isDrawing = false;
            this.saveToHistory(); // Сохраняем состояние после рисования
        }
    }
    
    drawPixel(gridX, gridY, color) {
        const x = gridX * this.pixelSize;
        const y = gridY * this.pixelSize;
        
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x, y, this.pixelSize, this.pixelSize);
    }
    
    floodFill(startX, startY, fillColor) {
        // Проверяем границы
        if (startX < 0 || startX >= this.gridSize || startY < 0 || startY >= this.gridSize) {
            return;
        }
        
        // Получаем цвет начальной точки
        const startColor = this.getPixelColor(startX, startY);
        
        // Если цвета одинаковые, ничего не делаем
        if (this.colorsEqual(startColor, fillColor)) {
            return;
        }
        
        // Ограничиваем количество итераций для предотвращения зависания
        const maxIterations = this.gridSize * this.gridSize;
        let iterations = 0;
        
        const stack = [{x: startX, y: startY}];
        const visited = new Set(); // Для отслеживания посещенных пикселей
        
        while (stack.length > 0 && iterations < maxIterations) {
            iterations++;
            
            const {x, y} = stack.pop();
            const key = `${x},${y}`;
            
            // Проверяем границы и посещение
            if (x < 0 || x >= this.gridSize || y < 0 || y >= this.gridSize || visited.has(key)) {
                continue;
            }
            
            // Проверяем цвет текущего пикселя
            if (!this.colorsEqual(this.getPixelColor(x, y), startColor)) {
                continue;
            }
            
            // Отмечаем как посещенный
            visited.add(key);
            
            // Заливаем пиксель
            this.drawPixel(x, y, fillColor);
            
            // Добавляем соседние пиксели в стек (только если они не посещены)
            const neighbors = [
                {x: x + 1, y: y},
                {x: x - 1, y: y},
                {x: x, y: y + 1},
                {x: x, y: y - 1}
            ];
            
            for (const neighbor of neighbors) {
                const neighborKey = `${neighbor.x},${neighbor.y}`;
                if (!visited.has(neighborKey)) {
                    stack.push(neighbor);
                }
            }
        }
        
        // Если достигли лимита итераций, выводим предупреждение
        if (iterations >= maxIterations) {
            console.warn('Заливка была ограничена для предотвращения зависания');
        }
    }
    
    getPixelColor(gridX, gridY) {
        const x = gridX * this.pixelSize + this.pixelSize / 2;
        const y = gridY * this.pixelSize + this.pixelSize / 2;
        
        const imageData = this.ctx.getImageData(x, y, 1, 1);
        const data = imageData.data;
        
        return `rgb(${data[0]}, ${data[1]}, ${data[2]})`;
    }
    
    colorsEqual(color1, color2) {
        // Нормализуем цвета для сравнения
        const normalizeColor = (color) => {
            if (color.startsWith('#')) {
                // Конвертируем hex в rgb
                const hex = color.slice(1);
                const r = parseInt(hex.slice(0, 2), 16);
                const g = parseInt(hex.slice(2, 4), 16);
                const b = parseInt(hex.slice(4, 6), 16);
                return `rgb(${r}, ${g}, ${b})`;
            }
            return color.toLowerCase();
        };
        
        return normalizeColor(color1) === normalizeColor(color2);
    }
    
    drawGrid() {
        this.ctx.strokeStyle = '#e0e0e0';
        this.ctx.lineWidth = 1;
        
        // Рисуем вертикальные линии
        for (let x = 0; x <= this.canvas.width; x += this.pixelSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        
        // Рисуем горизонтальные линии
        for (let y = 0; y <= this.canvas.height; y += this.pixelSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }
    
    clearCanvas() {
        this.ctx.fillStyle = '#ffffff';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawGrid();
        this.saveToHistory();
    }
    
    // Сохранение состояния в историю
    saveToHistory() {
        // Удаляем все действия после текущего индекса
        this.history = this.history.slice(0, this.historyIndex + 1);
        
        // Добавляем новое состояние
        const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
        this.history.push(imageData);
        this.historyIndex++;
        
        // Ограничиваем размер истории
        if (this.history.length > this.maxHistory) {
            this.history.shift();
            this.historyIndex--;
        }
        
        // Обновляем состояние кнопки отмены
        this.updateUndoButton();
    }
    
    // Отмена действия
    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            const imageData = this.history[this.historyIndex];
            this.ctx.putImageData(imageData, 0, 0);
            this.drawGrid(); // Перерисовываем сетку
            this.updateUndoButton();
        }
    }
    
    // Обновление состояния кнопки отмены
    updateUndoButton() {
        const undoBtn = document.getElementById('undo-action');
        if (undoBtn) {
            undoBtn.disabled = this.historyIndex <= 0;
            if (undoBtn.disabled) {
                undoBtn.style.opacity = '0.5';
                undoBtn.style.cursor = 'not-allowed';
            } else {
                undoBtn.style.opacity = '1';
                undoBtn.style.cursor = 'pointer';
            }
        }
    }
    
    downloadImage() {
        // Создаем временный холст для экспорта с увеличением 500%
        const tempCanvas = document.createElement('canvas');
        const tempCtx = tempCanvas.getContext('2d');
        
        // Устанавливаем размер 320x320 (64 * 5 = 320)
        tempCanvas.width = 320;
        tempCanvas.height = 320;
        
        // Рисуем изображение с масштабированием 500%
        tempCtx.imageSmoothingEnabled = false;
        tempCtx.drawImage(this.canvas, 0, 0, 320, 320);
        
        // Создаем ссылку для скачивания
        const link = document.createElement('a');
        link.download = 'pixel-art.png';
        link.href = tempCanvas.toDataURL();
        link.click();
    }
}

// Инициализация редактора после загрузки страницы
document.addEventListener('DOMContentLoaded', () => {
    new PixelArtEditor();
}); 