# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем curl для загрузки Poetry
RUN apt-get update && apt-get install -y curl

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

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