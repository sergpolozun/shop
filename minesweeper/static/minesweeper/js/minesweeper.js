// --- Minesweeper Game ---

const $ = id => document.getElementById(id);

// --- Game State ---
let width = 9, height = 9, mines = 10, timeLimit = 60;
let board = [], mineSet = new Set(), flagSet = new Set();
let timer = 0, timerInterval = null, opened = 0, gameOver = false, firstClick = true;

// --- Utility ---
function cellId(x, y) { return `${x}_${y}`; }
function inBounds(x, y) { return x >= 0 && x < width && y >= 0 && y < height; }
function neighbors(x, y) {
    const d = [-1, 0, 1];
    let res = [];
    for (let dx of d) for (let dy of d) {
        if (dx === 0 && dy === 0) continue;
        let nx = x + dx, ny = y + dy;
        if (inBounds(nx, ny)) res.push([nx, ny]);
    }
    return res;
}

// --- Board Rendering ---
function setBoardSize(w, h) {
    const boardDiv = $("ms-board");
    boardDiv.style.gridTemplateColumns = `repeat(${w}, 32px)`;
    boardDiv.style.gridTemplateRows = `repeat(${h}, 32px)`;
}

function renderBoard() {
    const boardDiv = $("ms-board");
    boardDiv.innerHTML = '';
    setBoardSize(width, height);
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const cell = document.createElement('div');
            cell.className = 'ms-cell';
            cell.id = cellId(x, y);
            cell.dataset.x = x;
            cell.dataset.y = y;
            cell.onmousedown = cellMouseDown;
            boardDiv.appendChild(cell);
        }
    }
}

// --- Game Logic ---
function placeMines(sx, sy) {
    mineSet.clear();
    let safe = new Set([cellId(sx, sy)]);
    for (let [nx, ny] of neighbors(sx, sy)) safe.add(cellId(nx, ny));
    let placed = 0;
    while (placed < mines) {
        let x = Math.floor(Math.random() * width);
        let y = Math.floor(Math.random() * height);
        let cid = cellId(x, y);
        if (!mineSet.has(cid) && !safe.has(cid)) {
            mineSet.add(cid);
            placed++;
        }
    }
}

function countMines(x, y) {
    return neighbors(x, y).filter(([nx, ny]) => mineSet.has(cellId(nx, ny))).length;
}

function openCell(x, y) {
    const cid = cellId(x, y);
    if (flagSet.has(cid) || board[y][x].open) return;
    board[y][x].open = true;
    opened++;
    const cell = $(cid);
    cell.classList.add('open');
    let minesAround = countMines(x, y);
    if (mineSet.has(cid)) {
        cell.classList.add('mine');
        cell.textContent = '💣';
        gameOver = true;
        showModal('Поражение', 'Вы подорвались на мине!');
        stopTimer();
        revealMines();
        return;
    }
    if (minesAround > 0) {
        cell.textContent = minesAround;
    } else {
        for (let [nx, ny] of neighbors(x, y)) {
            if (!board[ny][nx].open) openCell(nx, ny);
        }
    }
    if (opened === width * height - mines) {
        gameOver = true;
        showModal('Победа', 'Вы успешно разминировали поле!');
        stopTimer();
        revealMines(true);
    }
}

function revealMines(win=false) {
    for (let cid of mineSet) {
        const cell = $(cid);
        if (!cell.classList.contains('open')) {
            cell.classList.add('mine');
            cell.textContent = win ? '🚩' : '💣';
        }
    }
}

function toggleFlag(x, y) {
    const cid = cellId(x, y);
    const cell = $(cid);
    if (board[y][x].open) return;
    if (flagSet.has(cid)) {
        flagSet.delete(cid);
        cell.classList.remove('flag');
        cell.textContent = '';
    } else if (flagSet.size < mines) {
        flagSet.add(cid);
        cell.classList.add('flag');
        cell.textContent = '🚩';
    }
    $("ms-mines").textContent = mines - flagSet.size;
}

function cellMouseDown(e) {
    if (gameOver) return;
    const x = +this.dataset.x, y = +this.dataset.y;
    if (e.button === 0) { // ЛКМ
        if (firstClick) {
            startGame(x, y);
            firstClick = false;
        }
        openCell(x, y);
    } else if (e.button === 2) { // ПКМ
        toggleFlag(x, y);
    }
}

function startGame(sx, sy) {
    placeMines(sx, sy);
    startTimer();
}

function resetGame(w, h, m, t) {
    width = w; height = h; mines = m; timeLimit = t;
    board = Array.from({length: height}, () => Array.from({length: width}, () => ({open: false})));
    mineSet.clear();
    flagSet.clear();
    opened = 0;
    timer = timeLimit;
    gameOver = false;
    firstClick = true;
    $("ms-mines").textContent = mines;
    $("ms-timer").textContent = timer;
    stopTimer();
    renderBoard();
}

// --- Таймер (обратный отсчёт) ---
function startTimer() {
    stopTimer();
    timerInterval = setInterval(() => {
        timer--;
        $("ms-timer").textContent = timer;
        if (timer <= 0) {
            stopTimer();
            gameOver = true;
            showModal('Время вышло', 'Вы не успели разминировать поле!');
            revealMines();
        }
    }, 1000);
}
function stopTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = null;
}

// --- Модальное окно ---
function showModal(title, body) {
    $("ms-modal-title").textContent = title;
    $("ms-modal-body").textContent = body;
    $("ms-modal").style.display = '';
}
function closeMsModal() {
    $("ms-modal").style.display = 'none';
}
function startNewGame() {
    openDifficultyModal();
    closeMsModal();
}

// --- Модальное окно выбора сложности ---
function openDifficultyModal() {
    $("difficulty-modal").style.display = '';
}
function closeDifficultyModal() {
    $("difficulty-modal").style.display = 'none';
}

// --- UI ---
document.addEventListener('DOMContentLoaded', () => {
    // Открыть модалку выбора сложности при старте
    openDifficultyModal();

    // Кнопка "Новая игра"
    $("open-difficulty").onclick = openDifficultyModal;

    // Кнопки выбора сложности
    document.querySelectorAll('.difficulty-btn').forEach(btn => {
        btn.onclick = function() {
            const w = +this.dataset.w, h = +this.dataset.h, m = +this.dataset.m, t = +this.dataset.t;
            closeDifficultyModal();
            resetGame(w, h, m, t);
        };
    });

    // Отключаем контекстное меню на поле
    $("ms-board").addEventListener('contextmenu', e => e.preventDefault());
}); 