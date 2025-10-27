#!/bin/bash

# Ожидание готовности базы данных
echo "Waiting for database..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    echo "Database is unavailable - sleeping"
    sleep 1
done
echo "Database is up - executing command"

# Переход в директорию проекта Django
cd /app/library_project

# Создание миграций
echo "Making migrations..."
python manage.py makemigrations

# Применение миграций
echo "Applying migrations..."
python manage.py migrate

# Создание суперпользователя (если не существует)
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"

# Запуск сервера
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
