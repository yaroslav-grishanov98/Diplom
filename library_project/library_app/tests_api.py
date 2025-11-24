from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Author, Book, BookIssue, Comment, Rating


class UserRegistrationTest(APITestCase):
    """Тесты регистрации пользователя."""

    def test_user_registration(self):
        url = reverse("register")
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "password2": "strongpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("username", response.data)


class UserLoginTest(APITestCase):
    """Тесты аутентификации пользователя и получения JWT токена."""

    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "password2": "strongpassword123",
        }
        self.client.post(reverse("register"), self.user_data, format="json")

    def test_token_obtain(self):
        url = reverse("token_obtain_pair")
        data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class AuthorAPITest(APITestCase):
    """Тесты CRUD операций для модели Author."""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            "admin", "admin@example.com", "adminpass"
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.author_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "birth_date": "1980-05-05",
        }

    def test_create_author(self):
        url = reverse("author-list")
        response = self.client.post(url, self.author_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_authors(self):
        self.client.post(reverse("author-list"),
                         self.author_data, format="json")
        response = self.client.get(reverse("author-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class BookAPITest(APITestCase):
    """Тесты CRUD операций для модели Book."""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            "admin", "admin@example.com", "adminpass"
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.author = Author.objects.create(first_name="John", last_name="Doe")
        self.book_data = {
            "title": "Test Book",
            "author_ids": [self.author.id],
            "genre": "Fiction",
            "published_date": "2020-01-01",
            "description": "Test description",
        }

    def test_create_book(self):
        url = reverse("book-list")
        response = self.client.post(url, self.book_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_books(self):
        self.client.post(reverse("book-list"), self.book_data, format="json")
        response = self.client.get(reverse("book-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class CommentAPITest(APITestCase):
    """Тесты создания комментариев к книгам."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", password="pass12345")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.author = Author.objects.create(first_name="John", last_name="Doe")
        self.book = Book.objects.create(
            title="Test Book",
            genre="Fiction",
            published_date="2020-01-01",
            description="Desc",
        )
        self.book.authors.add(self.author)

    def test_create_comment(self):
        url = reverse("comment-list")
        data = {"book": self.book.id, "text": "Great book!"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class RatingAPITest(APITestCase):
    """Тесты создания и обновления рейтингов книг."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", password="pass12345")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.author = Author.objects.create(first_name="John", last_name="Doe")
        self.book = Book.objects.create(
            title="Test Book",
            genre="Fiction",
            published_date="2020-01-01",
            description="Desc",
        )
        self.book.authors.add(self.author)

    def test_create_rating(self):
        url = reverse("rating-list")
        data = {"book": self.book.id, "score": 4, "review": "Great book!"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unique_rating_per_user_book(self):
        url = reverse("rating-list")
        data = {"book": self.book.id, "score": 5, "review": "Awesome!"}
        self.client.post(url, data, format="json")
        response = self.client.post(url, data, format="json")
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN],
        )

    def test_delete_rating(self):
        url = reverse("rating-list")
        response = self.client.post(
            url, {"book": self.book.id, "score": 3, "review": "Good"}, format="json"
        )
        rating_id = response.data["id"]
        delete_url = reverse("rating-detail", args=[rating_id])
        response_delete = self.client.delete(delete_url)
        self.assertEqual(response_delete.status_code,
                         status.HTTP_204_NO_CONTENT)


class ProfileAPITest(APITestCase):
    """Тесты личного кабинета пользователя."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", password="pass12345")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.author = Author.objects.create(first_name="John", last_name="Doe")
        self.book = Book.objects.create(
            title="Test Book",
            genre="Fiction",
            published_date="2020-01-01",
            description="Desc",
        )
        self.book.authors.add(self.author)
        self.book_issue = BookIssue.objects.create(
            book=self.book, user=self.user, due_date="2099-12-31"
        )

    def test_profile_active_issues(self):
        self.client.login(username="user1", password="pass12345")
        url = reverse("profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.book.title)
