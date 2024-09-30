# Переменные для команд
DOCKER_COMPOSE = docker-compose
POETRY = poetry

# Команда для установки зависимостей
install:
	$(POETRY) install

# Команда для сборки и запуска всех сервисов через Docker Compose
up:
	$(DOCKER_COMPOSE) up --build

# Команда для остановки и удаления контейнеров
down:
	$(DOCKER_COMPOSE) down

# Команда для просмотра логов всех сервисов
logs:
	$(DOCKER_COMPOSE) logs -f

# Команда для выполнения миграций
migrate:
	$(POETRY) run alembic upgrade head

# Команда для запуска бота локально
run-bot:
	$(POETRY) run python bot.py

# Команда для запуска FastAPI локально
run-api:
	$(POETRY) run uvicorn client_api:app --host 0.0.0.0 --port 8000

# Команда для запуска обоих приложений (бот и API) в Docker
run-all:
	$(DOCKER_COMPOSE) up --build -d

# Команда для остановки всех приложений (бот, API)
stop-all:
	$(DOCKER_COMPOSE) down
