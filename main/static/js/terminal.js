class Terminal {
    constructor() {
        this.commands = {
            help: this.showHelp.bind(this),
            clear: this.clear.bind(this),
            about: this.showAbout.bind(this),
            date: this.showDate.bind(this),
            time: this.showTime.bind(this),
            echo: this.echo.bind(this),
            matrix: this.matrix.bind(this),
            ls: this.listFiles.bind(this),
            cat: this.catFile.bind(this),
            whoami: this.whoami.bind(this),
            pwd: this.pwd.bind(this),
            exit: this.exit.bind(this),
            sales: this.showSales.bind(this),
            news: this.showNews.bind(this),
            popular: this.showPopular.bind(this)
        };
        
        this.files = {
            'readme.txt': 'Добро пожаловать в POLOS Terminal!\n\nЭто терминал в стиле ретро-футуризма с отсылками к Матрице.\nИспользуйте команду "help" для списка доступных команд.',
            'matrix.txt': 'Добро пожаловать в Матрицу...\n\nВыберите красную таблетку или синюю таблетку.\nНо помните - выбор уже сделан.',
            'project.txt': 'POLOS - это проект, объединяющий ретро-стиль Windows 98\nс современными веб-технологиями.\n\nВключает в себя:\n- Магазин товаров\n- Графический редактор\n- Игру Сапёр\n- Систему смены обоев\n- Терминал (этот файл)'
        };
        
        this.currentUser = 'user@polos';
        this.currentDir = '/home/user';
        this.history = [];
        this.historyIndex = -1;
        this.isInitialized = false;
    }

    init() {
        console.log('POLOS_USERNAME:', window.POLOS_USERNAME);
        this.terminal = document.getElementById('terminalOutput');
        this.input = document.getElementById('terminalInput');
        
        // Очищаем терминал при каждом открытии
        this.terminal.innerHTML = '';
        this.input.removeEventListener('keydown', this.handleKeyDownBinded || (()=>{}));
        this.handleKeyDownBinded = this.handleKeyDown.bind(this);
        this.input.addEventListener('keydown', this.handleKeyDownBinded);
        
        // Устанавливаем username, если есть
        if (window.POLOS_USERNAME) {
            this.currentUser = window.POLOS_USERNAME + '@polos';
            this.currentDir = '/home/' + window.POLOS_USERNAME;
        } else {
            this.currentUser = 'user@polos';
            this.currentDir = '/home/user';
        }
        
        // Показываем приветствие и prompt только один раз
        this.typeWelcome();
        this.isInitialized = true;
    }

    async typeWelcome() {
        // Очищаем терминал перед анимацией
        this.terminal.innerHTML = '';
        // Формируем массив строк приветствия
        const welcomeLines = [];
        welcomeLines.push('Matrix-style interface initialized...');
        welcomeLines.push('Loading system components...');
        welcomeLines.push('System ready.');
        if (window.POLOS_USERNAME) {
            welcomeLines.push(`hello, ${window.POLOS_USERNAME}`);
        }
        welcomeLines.push('');
        welcomeLines.push("Type 'help' for available commands.");
        welcomeLines.push('');
        // Печатаем каждую строку с эффектом печати
        for (const line of welcomeLines) {
            await this.typeLine(line, 80); // скорость печати 80мс на символ
        }
        this.addLine(`${this.currentUser}:${this.currentDir}$ `);
        this.input.focus();
    }

    async typeLine(line, speed = 50) {
        if (line.trim() === '') {
            this.addLine('');
            return;
        }
        // Добавляем пустой div для анимации этой строки
        this.addLine('');
        let currentLine = '';
        for (let j = 0; j < line.length; j++) {
            currentLine += line[j];
            this.updateLastLine(currentLine);
            await this.sleep(speed);
        }
        // Не добавляем строку повторно!
    }

    updateLastLine(text) {
        const lines = this.terminal.children;
        if (lines.length > 0) {
            const lastLine = lines[lines.length - 1];
            lastLine.textContent = text;
        }
    }

    addLine(text) {
        const line = document.createElement('div');
        line.className = 'terminal-line';
        line.textContent = text;
        this.terminal.appendChild(line);
        this.terminal.scrollTop = this.terminal.scrollHeight;
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    handleKeyDown(e) {
        if (e.key === 'Enter') {
            const command = this.input.value.trim();
            this.input.value = '';
            
            if (command) {
                this.history.push(command);
                this.historyIndex = this.history.length;
                this.executeCommand(command);
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.navigateHistory(-1);
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.navigateHistory(1);
        }
    }

    navigateHistory(direction) {
        if (this.history.length === 0) return;
        
        this.historyIndex += direction;
        
        if (this.historyIndex < 0) {
            this.historyIndex = 0;
        } else if (this.historyIndex >= this.history.length) {
            this.historyIndex = this.history.length;
            this.input.value = '';
            return;
        }
        
        this.input.value = this.history[this.historyIndex];
    }

    executeCommand(command) {
        const parts = command.split(' ');
        const cmd = parts[0].toLowerCase();
        const args = parts.slice(1);

        this.addLine(`${this.currentUser}:${this.currentDir}$ ${command}`);

        if (this.commands[cmd]) {
            this.commands[cmd](args);
        } else {
            this.addLine(`bash: ${cmd}: command not found`);
        }

        this.addLine(`${this.currentUser}:${this.currentDir}$ `);
    }

    showHelp() {
        const helpLines = [
            'help     - Show this help message',
            'clear    - Clear terminal screen',
            'about    - Show project information',
            'date     - Show current date',
            'time     - Show current time',
            'echo     - Print arguments',
            'matrix   - Matrix-style animation',
            'ls       - List files',
            'cat      - Display file contents',
            'whoami   - Show current user',
            'pwd      - Show current directory',
            'sales    - Show 3 sale products',
            'news     - Show 3 new products',
            'popular  - Show 3 most popular products',
            'exit     - Close terminal',
            '',
            "Type 'help <command>' for more information about a specific command."
        ];
        helpLines.forEach(line => this.addLine(line));
    }

    clear() {
        this.terminal.innerHTML = '';
        this.addLine(`${this.currentUser}:${this.currentDir}$ `);
    }

    showAbout() {
        const aboutText = `POLOS Terminal v1.0.0
========================

POLOS - это проект, объединяющий ретро-стиль Windows 98 
с современными веб-технологиями.

Особенности:
- Матричная анимация бегущей строки
- Система команд в стиле Unix/Linux
- Интеграция с рабочим столом POLOS
- Поддержка истории команд

Вдохновлено фильмом "Матрица" и классическими терминалами.

Автор: POLOS Development Team
Лицензия: MIT`;
        
        this.addLine(aboutText);
    }

    showDate() {
        const date = new Date().toLocaleDateString('ru-RU');
        this.addLine(date);
    }

    showTime() {
        const time = new Date().toLocaleTimeString('ru-RU');
        this.addLine(time);
    }

    echo(args) {
        this.addLine(args.join(' '));
    }

    matrix() {
        this.addLine('Entering Matrix mode...');
        this.addLine('Wake up, Neo...');
        this.addLine('The Matrix has you...');
        this.addLine('Follow the white rabbit...');
        this.addLine('Knock, knock, Neo...');
    }

    listFiles() {
        const fileList = Object.keys(this.files).join('  ');
        this.addLine(fileList);
    }

    catFile(args) {
        if (args.length === 0) {
            this.addLine('cat: missing file operand');
            return;
        }
        
        const filename = args[0];
        if (this.files[filename]) {
            this.addLine(this.files[filename]);
        } else {
            this.addLine(`cat: ${filename}: No such file or directory`);
        }
    }

    whoami() {
        this.addLine(this.currentUser);
    }

    pwd() {
        this.addLine(this.currentDir);
    }

    exit() {
        closeModal('terminalModal');
    }

    async showSales() {
        this.addLine('Топ-3 товара со статусом "распродажа":');
        try {
            const resp = await fetch('/shop/api/terminal/sales/');
            const data = await resp.json();
            if (data.products.length === 0) {
                this.addLine('Нет товаров со статусом "распродажа".');
            } else {
                data.products.forEach(p => this.addLine(`${p.name} — ${p.price}₽`));
            }
        } catch (e) {
            this.addLine('Ошибка получения данных.');
        }
    }

    async showNews() {
        this.addLine('Топ-3 новых товара:');
        try {
            const resp = await fetch('/shop/api/terminal/news/');
            const data = await resp.json();
            if (data.products.length === 0) {
                this.addLine('Нет новых товаров.');
            } else {
                data.products.forEach(p => this.addLine(`${p.name} — ${p.price}₽`));
            }
        } catch (e) {
            this.addLine('Ошибка получения данных.');
        }
    }

    async showPopular() {
        this.addLine('Топ-3 популярных товара:');
        try {
            const resp = await fetch('/shop/api/terminal/popular/');
            const data = await resp.json();
            if (data.products.length === 0) {
                this.addLine('Нет популярных товаров.');
            } else {
                data.products.forEach(p => this.addLine(`${p.name} — ${p.price}₽`));
            }
        } catch (e) {
            this.addLine('Ошибка получения данных.');
        }
    }
}

// Инициализация терминала при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const terminal = new Terminal();
    
    // Глобальная функция для открытия терминала
    window.openTerminal = function() {
        openModal('terminalModal');
        setTimeout(() => {
            terminal.init();
        }, 100);
    };
}); 