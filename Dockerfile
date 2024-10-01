# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем curl для загрузки Poetry
RUN apt-get update && apt-get install -y curl

# Устанавливаем pip и Poetry через pip
RUN pip install --upgrade pip
RUN pip install poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл pyproject.toml и poetry.lock
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости через Poetry
RUN poetry install --no-root

# Копируем все файлы проекта в контейнер
COPY . .

# Запуск FastAPI (или бота) в зависимости от нужд
CMD ["poetry", "run", "uvicorn", "client_api:app", "--host", "0.0.0.0", "--port", "8000"]