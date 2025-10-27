# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY library_project/ ./library_project/

# Копируем скрипт инициализации
COPY entrypoint.sh /app/entrypoint.sh

# Делаем скрипт исполняемым
RUN chmod +x /app/entrypoint.sh

# Устанавливаем рабочую директорию для Django проекта
WORKDIR /app/library_project

# Открываем порт
EXPOSE 8000

# Команда для запуска приложения
ENTRYPOINT ["/app/entrypoint.sh"]
