# Library API

## Описание
REST API для управления библиотекой, включающий управление книгами, авторами, пользователями и выдачей книг. Проект реализован с использованием Django и Django REST Framework, с поддержкой JWT аутентификации и контейнеризацией через Docker.

## Технологии
- Python 3.11
- Django 4.x
- Django REST Framework
- PostgreSQL
- Docker и Docker Compose
- JWT аутентификация (SimpleJWT)
- Автоматическая документация API (Swagger, Redoc)

## Структура проекта
Diplom/
├── library_project/         # Основной проект Django
│   ├── settings.py          # Настройки проекта
│   ├── urls.py              # Основные маршруты
│   └── ...
├── library_app/             # Приложение с моделями и API
│   ├── models.py            # Модели (Книги, Авторы, Выдачи, Комментарии, Рейтинги)
│   ├── views.py             # Вьюхи и API вьюсеты
│   ├── serializers.py       # Сериализаторы DRF
│   ├── urls.py              # Маршруты приложения
│   ├── templates/           # Django шаблоны для фронтенда
│   ├── tests_api.py         # Тесты API
│   ├── tests_web.py         # Тесты веб-вьюх
│   └── ...
├── Dockerfile               # Docker образ для Django приложения
├── docker-compose.yml       # Конфигурация Docker Compose
├── requirements.txt         # Зависимости проекта
├── README.md                # Описание проекта

## Установка и запуск

### Предварительные условия
- Установлен Docker и Docker Compose
- Git

### Клонирование репозитория

```bash
git clone https://github.com/yaroslav-grishanov98/library_project.git
cd library_project
```

### Запуск проекта через Docker
- docker compose up -d --build

### Применение миграций
- docker compose exec web python manage.py migrate

### Создание суперпользователя
- docker compose exec web python manage.py createsuperuser

### Доступ к приложению
- Веб-интерфейс: http://localhost:8000/
- Админка Django: http://localhost:8000/admin/
- Документация API (Swagger): http://localhost:8000/swagger/
- Документация API (Redoc): http://localhost:8000/redoc/

### Использование API
- Регистрация: POST /register/
- Получение JWT токена: POST /token/
- Обновление JWT токена: POST /token/refresh/
- CRUD для авторов: /api/authors/
- CRUD для книг: /api/books/
- CRUD для выдач книг: /api/issues/
- CRUD для комментариев: /api/comments/
- CRUD для рейтингов: /api/ratings/

### Тестирование
- docker compose exec web python manage.py test

### Приложение library_app

## admin.py

# Класс AuthorAdmin
- Админ-класс для модели Author.

# Класс BookAdmin
- Админ-класс для модели Book.

# Класс BookIssueAdmin
- Админ-класс для модели BookIssue.

## forms.py

# Класс BookForm
- Форма для создания и редактирования модели Book

# Класс AuthorForm
- Форма для создания и редактирования модели Author

## models.py

# Класс Author
- Модель автора книги

# Класс Book
- Модель книги

# Класс BookIssue
- Модель выдачи книги пользователю

# Класс Rating
- Модель рейтинга книги

# Класс Comment
- Модель комментария к книге

## permissions.py

# Класс IsAdminOrReadOnly
- Разрешает полный доступ только администраторам, остальные могут только читать

# Класс IsOwnerOrAdmin
- Разрешает доступ к объектам только их владельцу или администратору

# Класс IsOwnerOrReadOnly
- Позволяет владельцу объекта изменять его, остальные — только читать

## serializers.py

# Класс AuthorSerializer
- Сериализатор для модели Author

# Класс BookSerializer
- Сериализатор для модели Book

# Класс UserSerializer
- Сериализатор для модели User

# Класс RegisterSerializer
- Сериализатор для регистрации пользователя

# Класс BookIssueSerializer
- Сериализатор для модели BookIssue

# Класс CommentSerializer
- Сериализатор для модели Comment

# Класс RatingSerializer
- Сериализатор для модели Rating

## test_api.py

# Класс UserRegistrationTest
- Тесты регистрации пользователя

# Класс UserLoginTest
- Тесты аутентификации пользователя и получения JWT токена

# Класс AuthorAPITest
- Тесты CRUD операций для модели Author

# Класс BookAPITest
- Тесты CRUD операций для модели Book

# Класс CommentAPITest
- Тесты создания комментариев к книгам

# Класс RatingAPITest
- Тесты создания и обновления рейтингов книг

# Класс ProfileAPITest
- Тесты личного кабинета пользователя

## test_web.py

# Класс AuthorWebTest
- Тесты веб-интерфейса для модели Author

# Класс BookWebTest
- Тесты веб-интерфейса для модели Book

# Класс ProfileWebTest
- Тесты веб-интерфейса для страницы профиля пользователя

## views.py

# Класс RegisterView
- API-вью для регистрации пользователей

# Класс RegisterPageView
- Веб-вью для регистрации через HTML форму

# Класс UserViewSet
- Вьюсет для просмотра пользователей

# Класс AuthorViewSet
- Вьюсет для CRUD операций с авторами

# Класс BookViewSet
- Вьюсет для CRUD операций с книгами

# Класс BookIssueViewSet
- Вьюсет для управления выдачами книг

# Класс CommentViewSet
- API-вьюсет для комментариев

# Класс RatingViewSet
- API-вьюсет для рейтингов



   