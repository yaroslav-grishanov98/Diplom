from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Author, Book, BookIssue


class AuthorWebTest(TestCase):
    """Тесты веб-интерфейса для модели Author."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            "admin", "admin@example.com", "adminpass"
        )
        self.user = User.objects.create_user(
            "user", "user@example.com", "userpass")
        self.author = Author.objects.create(first_name="John", last_name="Doe")

    def test_delete_author_as_admin(self):
        self.client.login(username="admin", password="adminpass")
        url = reverse("author_delete", args=[self.author.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [302, 200])  # редирект или успех

    def test_delete_author_as_user(self):
        self.client.login(username="user", password="userpass")
        url = reverse("author_delete", args=[self.author.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [302, 403])  # редирект или отказ


class BookWebTest(TestCase):
    """Тесты веб-интерфейса для модели Book."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            "admin", "admin@example.com", "adminpass"
        )
        self.user = User.objects.create_user(
            "user", "user@example.com", "userpass")
        self.author = Author.objects.create(first_name="John", last_name="Doe")
        self.book = Book.objects.create(
            title="Test Book",
            genre="Fiction",
            published_date="2020-01-01",
            description="Desc",
        )
        self.book.authors.add(self.author)

    def test_delete_book_as_admin(self):
        self.client.login(username="admin", password="adminpass")
        url = reverse("book_delete", args=[self.book.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [302, 200])  # редирект или успех

    def test_delete_book_as_user(self):
        self.client.login(username="user", password="userpass")
        url = reverse("book_delete", args=[self.book.id])
        response = self.client.post(url)
        self.assertIn(response.status_code, [302, 403])  # редирект или отказ


class ProfileWebTest(TestCase):
    """Тесты веб-интерфейса для страницы профиля пользователя."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="user1", password="pass123")
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
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

    def test_profile_shows_active_issues(self):
        self.client.login(username="user1", password="pass123")
        response = self.client.get(reverse("profile"))
        self.assertContains(response, self.book.title)

    def test_profile_shows_no_issues_message(self):
        self.book_issue.return_date = timezone.now()
        self.book_issue.save()
        self.client.login(username="user1", password="pass123")
        response = self.client.get(reverse("profile"))
        self.assertContains(response, "You have not rented any books.")
