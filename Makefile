# ========================= LLM Learning System Makefile =========================
# Управление системой обучения с ИИ
# Использование: make [команда]
# Для просмотра всех команд: make help

.PHONY: help install setup-env parse-kb run-backend dev clean test db-init db-reset db-backup db-restore logs status check-deps

# Настройки
PYTHON = python3
PIP = pip
VENV = venv
BACKEND_HOST = 0.0.0.0
BACKEND_PORT = 8000
DATABASE_FILE = learning_system.db
KNOWLEDGE_BASE_PATH = ./knowledge_base
LOGS_DIR = logs
BACKUP_DIR = backups

# Цвета для вывода
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
PURPLE = \033[0;35m
CYAN = \033[0;36m
WHITE = \033[1;37m
NC = \033[0m # No Color

# ========================= ОСНОВНЫЕ КОМАНДЫ =========================

## Показать справку
help:
	@echo "$(CYAN)🚀 LLM Learning System - Makefile Commands$(NC)"
	@echo ""
	@echo "$(WHITE)📦 Установка и настройка:$(NC)"
	@echo "  $(GREEN)make install$(NC)     - Установить все зависимости"
	@echo "  $(GREEN)make setup-env$(NC)   - Настроить окружение (.env файл)"
	@echo "  $(GREEN)make check-deps$(NC)  - Проверить зависимости"
	@echo ""
	@echo "$(WHITE)🗃️ Database:$(NC)"
	@echo "  $(GREEN)make db-init$(NC)     - Инициализировать базу данных"
	@echo "  $(GREEN)make db-reset$(NC)    - Сбросить базу данных"
	@echo "  $(GREEN)make db-backup$(NC)   - Создать резервную копию БД"
	@echo "  $(GREEN)make db-restore$(NC)  - Восстановить БД из резервной копии"
	@echo ""
	@echo "$(WHITE)📚 База знаний:$(NC)"
	@echo "  $(GREEN)make parse-kb$(NC)    - Парсить базу знаний в БД"
	@echo "  $(GREEN)make create-kb$(NC)   - Создать пример базы знаний"
	@echo ""
	@echo "$(WHITE)🔧 Запуск:$(NC)"
	@echo "  $(GREEN)make run-backend$(NC) - Запустить бэкенд сервер"
	@echo "  $(GREEN)make dev$(NC)         - Запустить в режиме разработки"
	@echo "  $(GREEN)make prod$(NC)        - Запустить в продакшене"
	@echo ""
	@echo "$(WHITE)🧹 Утилиты:$(NC)"
	@echo "  $(GREEN)make clean$(NC)       - Очистить временные файлы"
	@echo "  $(GREEN)make test$(NC)        - Запустить тесты"
	@echo "  $(GREEN)make logs$(NC)        - Показать логи"
	@echo "  $(GREEN)make status$(NC)      - Показать статус системы"
	@echo "  $(GREEN)make requirements$(NC) - Обновить requirements.txt"
	@echo ""
	@echo "$(WHITE)🔍 Разработка:$(NC)"
	@echo "  $(GREEN)make lint$(NC)        - Проверить код линтером"
	@echo "  $(GREEN)make format$(NC)      - Форматировать код"
	@echo "  $(GREEN)make shell$(NC)       - Запустить Python shell"
	@echo ""

# ========================= УСТАНОВКА И НАСТРОЙКА =========================

## Установить все зависимости
install: check-python
	@echo "$(YELLOW)📦 Установка зависимостей...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt 2>/dev/null || $(PIP) install fastapi uvicorn openai bcrypt pyjwt python-multipart
	@echo "$(GREEN)✅ Зависимости установлены$(NC)"

## Настроить файл окружения
setup-env:
	@echo "$(YELLOW)⚙️  Настройка окружения...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(CYAN)📝 Создание .env файла...$(NC)"; \
		echo "# LLM Learning System Environment" > .env; \
		echo "OPENAI_API_KEY=your-openai-api-key-here" >> .env; \
		echo "SECRET_KEY=$$(openssl rand -hex 32)" >> .env; \
		echo "DATABASE_URL=sqlite:///$(DATABASE_FILE)" >> .env; \
		echo "KNOWLEDGE_BASE_PATH=$(KNOWLEDGE_BASE_PATH)" >> .env; \
		echo "BACKEND_HOST=$(BACKEND_HOST)" >> .env; \
		echo "BACKEND_PORT=$(BACKEND_PORT)" >> .env; \
		echo "$(GREEN)✅ Файл .env создан$(NC)"; \
		echo "$(YELLOW)⚠️  Не забудьте установить ваш OPENAI_API_KEY в .env$(NC)"; \
	else \
		echo "$(BLUE)ℹ️  Файл .env уже существует$(NC)"; \
	fi

## Проверить зависимости
check-deps:
	@echo "$(YELLOW)🔍 Проверка зависимостей...$(NC)"
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)❌ Python3 не найден$(NC)"; exit 1; }
	@command -v pip3 >/dev/null 2>&1 || { echo "$(RED)❌ pip3 не найден$(NC)"; exit 1; }
	@$(PYTHON) -c "import fastapi, uvicorn, openai, bcrypt, jwt" 2>/dev/null || { echo "$(RED)❌ Не все Python пакеты установлены. Запустите: make install$(NC)"; exit 1; }
	@echo "$(GREEN)✅ Все зависимости в порядке$(NC)"

check-python:
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)❌ Python3 не найден. Установите Python 3.8+$(NC)"; exit 1; }

# ========================= БАЗА ДАННЫХ =========================

## Инициализировать базу данных
db-init:
	@echo "$(YELLOW)🗃️ Инициализация базы данных...$(NC)"
	@$(PYTHON) -c "from backend import Database; db = Database(); print('База данных инициализирована')"
	@echo "$(GREEN)✅ База данных готова$(NC)"

## Сбросить базу данных
db-reset:
	@echo "$(YELLOW)🗃️ Сброс базы данных...$(NC)"
	@read -p "Вы уверены, что хотите сбросить базу данных? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -f $(DATABASE_FILE); \
		$(MAKE) db-init; \
		echo "$(GREEN)✅ База данных сброшена$(NC)"; \
	else \
		echo "$(BLUE)ℹ️  Операция отменена$(NC)"; \
	fi

## Создать резервную копию БД
db-backup:
	@echo "$(YELLOW)💾 Создание резервной копии...$(NC)"
	@mkdir -p $(BACKUP_DIR)
	@if [ -f $(DATABASE_FILE) ]; then \
		cp $(DATABASE_FILE) $(BACKUP_DIR)/$(DATABASE_FILE)_backup_$$(date +%Y%m%d_%H%M%S); \
		echo "$(GREEN)✅ Резервная копия создана в $(BACKUP_DIR)$(NC)"; \
	else \
		echo "$(RED)❌ Файл базы данных не найден$(NC)"; \
	fi

## Восстановить БД из резервной копии
db-restore:
	@echo "$(YELLOW)🔄 Восстановление базы данных...$(NC)"
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)❌ Укажите файл резервной копии: make db-restore BACKUP_FILE=path/to/backup$(NC)"; \
		exit 1; \
	fi
	@if [ -f "$(BACKUP_FILE)" ]; then \
		cp "$(BACKUP_FILE)" $(DATABASE_FILE); \
		echo "$(GREEN)✅ База данных восстановлена$(NC)"; \
	else \
		echo "$(RED)❌ Файл резервной копии не найден$(NC)"; \
	fi

# ========================= БАЗА ЗНАНИЙ =========================

## Парсить базу знаний
parse-kb: check-deps
	@echo "$(YELLOW)📚 Парсинг базы знаний...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Файл .env не найден. Запустите: make setup-env$(NC)"; \
		exit 1; \
	fi
	@if [ ! -d $(KNOWLEDGE_BASE_PATH) ]; then \
		echo "$(YELLOW)⚠️  Папка базы знаний не найдена. Создаю пример...$(NC)"; \
		$(MAKE) create-kb; \
	fi
	@export $$(cat .env | grep -v '^#' | xargs) && $(PYTHON) parse.py
	@echo "$(GREEN)✅ Парсинг завершен$(NC)"

## Создать пример базы знаний
create-kb:
	@echo "$(YELLOW)📝 Создание примера базы знаний...$(NC)"
	@mkdir -p $(KNOWLEDGE_BASE_PATH)/python_basics
	@echo "# Введение в Python\n\nПython - это мощный язык программирования." > $(KNOWLEDGE_BASE_PATH)/python_basics/intro.md
	@echo "# План обучения\n\n1. Основы синтаксиса\n2. Переменные и типы данных\n3. Функции" > $(KNOWLEDGE_BASE_PATH)/python_basics/edu-plan.md
	@echo "# Блок 1: Основы синтаксиса\n\n## Переменные\n\nВ Python переменные создаются просто:\n\n\`\`\`python\nname = 'Python'\nversion = 3.9\n\`\`\`" > $(KNOWLEDGE_BASE_PATH)/python_basics/block-01-syntax.md
	@echo "$(GREEN)✅ Пример базы знаний создан в $(KNOWLEDGE_BASE_PATH)$(NC)"

# ========================= ЗАПУСК =========================

## Запустить бэкенд сервер
run-backend: check-deps
	@echo "$(YELLOW)🚀 Запуск бэкенда...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Файл .env не найден. Запустите: make setup-env$(NC)"; \
		exit 1; \
	fi
	@if [ ! -f $(DATABASE_FILE) ]; then \
		echo "$(YELLOW)⚠️  База данных не найдена. Инициализирую...$(NC)"; \
		$(MAKE) db-init; \
	fi
	@echo "$(GREEN)🌟 Сервер запущен на http://$(BACKEND_HOST):$(BACKEND_PORT)$(NC)"
	@echo "$(GREEN)📖 Документация доступна на http://$(BACKEND_HOST):$(BACKEND_PORT)/docs$(NC)"
	@export $$(cat .env | grep -v '^#' | xargs) && $(PYTHON) backend.py

## Запустить в режиме разработки
dev: check-deps
	@echo "$(YELLOW)🔧 Запуск в режиме разработки...$(NC)"
	@mkdir -p $(LOGS_DIR)
	@if [ ! -f .env ]; then $(MAKE) setup-env; fi
	@if [ ! -f $(DATABASE_FILE) ]; then $(MAKE) db-init; fi
	@export $$(cat .env | grep -v '^#' | xargs) && $(PYTHON) backend.py --reload --log-level debug

## Запустить в продакшене
prod: check-deps
	@echo "$(YELLOW)🚀 Запуск в продакшене...$(NC)"
	@mkdir -p $(LOGS_DIR)
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Файл .env не найден для продакшена$(NC)"; \
		exit 1; \
	fi
	@export $$(cat .env | grep -v '^#' | xargs) && \
	uvicorn backend:app --host $(BACKEND_HOST) --port $(BACKEND_PORT) --workers 4 \
		--log-file $(LOGS_DIR)/app.log --access-log --no-use-colors

# ========================= УТИЛИТЫ =========================

## Очистить временные файлы
clean:
	@echo "$(YELLOW)🧹 Очистка временных файлов...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf .pytest_cache 2>/dev/null || true
	@rm -rf htmlcov 2>/dev/null || true
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

## Показать логи
logs:
	@echo "$(YELLOW)📋 Логи системы:$(NC)"
	@if [ -f $(LOGS_DIR)/app.log ]; then \
		tail -f $(LOGS_DIR)/app.log; \
	else \
		echo "$(BLUE)ℹ️  Файл логов не найден$(NC)"; \
	fi

## Показать статус системы
status:
	@echo "$(CYAN)📊 Статус LLM Learning System:$(NC)"
	@echo ""
	@echo "$(WHITE)📁 Файлы:$(NC)"
	@echo "  База данных: $(if $(shell test -f $(DATABASE_FILE) && echo 1),$(GREEN)✅ Найдена$(NC),$(RED)❌ Не найдена$(NC))"
	@echo "  База знаний: $(if $(shell test -d $(KNOWLEDGE_BASE_PATH) && echo 1),$(GREEN)✅ Найдена$(NC),$(RED)❌ Не найдена$(NC))"
	@echo "  Конфигурация: $(if $(shell test -f .env && echo 1),$(GREEN)✅ Найдена$(NC),$(RED)❌ Не найдена$(NC))"
	@echo ""
	@echo "$(WHITE)📊 Статистика БД:$(NC)"
	@if [ -f $(DATABASE_FILE) ]; then \
		echo "  $$(sqlite3 $(DATABASE_FILE) 'SELECT COUNT(*) FROM topics;' 2>/dev/null || echo 0) тем"; \
		echo "  $$(sqlite3 $(DATABASE_FILE) 'SELECT COUNT(*) FROM blocks;' 2>/dev/null || echo 0) блоков"; \
		echo "  $$(sqlite3 $(DATABASE_FILE) 'SELECT COUNT(*) FROM students;' 2>/dev/null || echo 0) студентов"; \
	else \
		echo "  $(RED)База данных не найдена$(NC)"; \
	fi

## Запустить тесты
test:
	@echo "$(YELLOW)🧪 Запуск тестов...$(NC)"
	@$(PYTHON) -m pytest tests/ -v 2>/dev/null || echo "$(BLUE)ℹ️  Тесты не найдены. Создайте папку tests/$(NC)"

## Обновить requirements.txt
requirements:
	@echo "$(YELLOW)📝 Обновление requirements.txt...$(NC)"
	@$(PIP) freeze > requirements.txt
	@echo "$(GREEN)✅ requirements.txt обновлен$(NC)"

# ========================= РАЗРАБОТКА =========================

## Проверить код линтером
lint:
	@echo "$(YELLOW)🔍 Проверка кода...$(NC)"
	@$(PYTHON) -m flake8 *.py 2>/dev/null || echo "$(BLUE)ℹ️  flake8 не установлен. Установите: pip install flake8$(NC)"

## Форматировать код
format:
	@echo "$(YELLOW)🎨 Форматирование кода...$(NC)"
	@$(PYTHON) -m black *.py 2>/dev/null || echo "$(BLUE)ℹ️  black не установлен. Установите: pip install black$(NC)"

## Запустить Python shell
shell:
	@echo "$(YELLOW)🐍 Запуск Python shell...$(NC)"
	@$(PYTHON) -i -c "from backend import *; print('Backend модули загружены')"

# ========================= СОСТАВНЫЕ КОМАНДЫ =========================

## Полная настройка проекта
setup: install setup-env create-kb db-init
	@echo "$(GREEN)🎉 Проект настроен! Теперь можете запустить: make dev$(NC)"

## Быстрый старт
quickstart: setup parse-kb
	@echo "$(GREEN)🚀 Быстрый старт завершен! Запускаю сервер...$(NC)"
	@$(MAKE) run-backend

## Обновить всё
update: install requirements clean
	@echo "$(GREEN)🔄 Обновление завершено$(NC)"

# ========================= СПЕЦИАЛЬНЫЕ ПРАВИЛА =========================

# Автоматическое создание директорий
$(LOGS_DIR):
	@mkdir -p $(LOGS_DIR)

$(BACKUP_DIR):
	@mkdir -p $(BACKUP_DIR)

# Правило по умолчанию
.DEFAULT_GOAL := help