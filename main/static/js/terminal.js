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
            exit: this.exit.bind(this)
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
        this.terminal = document.getElementById('terminalOutput');
        this.input = document.getElementById('terminalInput');
        
        // Очищаем терминал при повторном входе
        if (this.isInitialized) {
            this.terminal.innerHTML = '';
        }
        
        this.input.addEventListener('keydown', this.handleKeyDown.bind(this));
        
        // Запускаем анимацию приветствия только при первом входе
        if (!this.isInitialized) {
            this.typeWelcome();
            this.isInitialized = true;
        } else {
            // При повторном входе просто показываем промпт
            this.addLine(`${this.currentUser}:${this.currentDir}$ `);
            this.input.focus();
        }
    }

    async typeWelcome() {
        const welcomeText = `Welcome to POLOS Terminal v1.0.0
Matrix-style interface initialized...
Loading system components...
System ready.

Type 'help' for available commands.

${this.currentUser}:${this.currentDir}$ `;
        
        await this.typeText(welcomeText);
        this.input.focus();
    }

    async typeText(text, speed = 50) {
        const lines = text.split('\n');
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line.includes('$')) {
                // Это строка с промптом - печатаем сразу
                this.addLine(line);
            } else {
                // Обычная строка - печатаем посимвольно
                let currentLine = '';
                for (let j = 0; j < line.length; j++) {
                    currentLine += line[j];
                    this.updateLastLine(currentLine);
                    await this.sleep(speed);
                }
                this.addLine(line);
            }
        }
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
        const helpText = `Available commands:
  help     - Show this help message
  clear    - Clear terminal screen
  about    - Show project information
  date     - Show current date
  time     - Show current time
  echo     - Print arguments
  matrix   - Matrix-style animation
  ls       - List files
  cat      - Display file contents
  whoami   - Show current user
  pwd      - Show current directory
  exit     - Close terminal

Type 'help <command>' for more information about a specific command.`;
        
        this.addLine(helpText);
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