-- Инициализация базы данных для Django проекта
-- Этот файл выполняется автоматически при первом запуске PostgreSQL контейнера

-- Создание базы данных (если не существует)
SELECT 'CREATE DATABASE diplom'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'diplom')\gexec

-- Предоставление всех привилегий пользователю
GRANT ALL PRIVILEGES ON DATABASE diplom TO yaroslav;

-- Создание расширений, которые могут понадобиться Django
\c diplom;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Установка правильной схемы по умолчанию
ALTER DATABASE diplom SET search_path TO public;
