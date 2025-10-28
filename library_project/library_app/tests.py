from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from rest_framework import status
from .models import Author, Book
import io
from PIL import Image


class UserRegistrationTest(APITestCase):
    def test_user_registration(self):
        url = reverse('register')
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "password2": "strongpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', response.data)

class UserLoginTest(APITestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "password2": "strongpassword123"
        }
        self.client.post(reverse('register'), self.user_data, format='json')

    def test_token_obtain(self):
        url = reverse('token_obtain_pair')
        data = {
            "username": self.user_data['username'],
            "password": self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class AuthorAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.author = Author.objects.create(first_name='John', last_name='Doe')
        self.author_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "birth_date": "1980-05-05"
        }

    def test_create_author(self):
        url = reverse('author-list')
        response = self.client.post(url, self.author_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], self.author_data['first_name'])

    def test_get_authors(self):
        response = self.client.get(reverse('author-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_author(self):
        url = reverse('author-detail', args=[self.author.id])
        data = {"first_name": "Jane", "last_name": "Smith", "birth_date": "1980-05-05"}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "Jane")

    def test_delete_author(self):
        url = reverse('author-detail', args=[self.author.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class BookAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.author = Author.objects.create(first_name='John', last_name='Doe')
        self.book = Book.objects.create(
            title='Old Title',
            genre='Fiction',
            published_date='2020-01-01',
            description='Old description'
        )
        self.book.authors.add(self.author)
        self.book_data = {
            "title": "New Title",
            "author_ids": [self.author.id],
            "genre": "Non-fiction",
            "published_date": "2021-01-01",
            "description": "New description"
        }

    def test_create_book(self):
        url = reverse('book-list')
        response = self.client.post(url, self.book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.book_data['title'])

    def test_get_books(self):
        self.client.post(reverse('book-list'), self.book_data, format='json')
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_book(self):
        url = reverse('book-detail', args=[self.book.id])
        response = self.client.put(url, self.book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "New Title")

    def test_delete_book(self):
        url = reverse('book-detail', args=[self.book.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class AuthorPermissionTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='userpass123')
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.author = Author.objects.create(first_name='John', last_name='Doe')

    def test_user_cannot_create_author(self):
        url = reverse('author-list')
        data = {"first_name": "Jane", "last_name": "Smith"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_update_author(self):
        url = reverse('author-detail', args=[self.author.id])
        data = {"first_name": "Jane"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_author(self):
        url = reverse('author-detail', args=[self.author.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class UserRegistrationNegativeTest(APITestCase):
    def test_passwords_must_match(self):
        url = reverse('register')
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "password2": "password456"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserLoginNegativeTest(APITestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "password2": "password123"
        }
        self.client.post(reverse('register'), self.user_data, format='json')

    def test_login_with_wrong_password(self):
        url = reverse('token_obtain_pair')
        data = {
            "username": self.user_data['username'],
            "password": "wrongpassword"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BookImageUploadTest(APITestCase):
    def setUp(self):
        # Создаем суперпользователя и аутентифицируемся
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        # Создаем автора
        self.author = Author.objects.create(first_name='John', last_name='Doe')

    def generate_image_file(self):
        # Создаем временный файл изображения в памяти
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), 'blue')
        image.save(file, 'JPEG')
        file.name = 'test.jpg'
        file.seek(0)
        return file

    def test_upload_book_cover(self):
        url = reverse('book-list')
        image_file = self.generate_image_file()
        data = {
            "title": "Book with cover",
            "author_ids": [self.author.id],
            "genre": "Fiction",
            "published_date": "2020-01-01",
            "description": "Book with image cover",
            "cover": image_file
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertIn('cover', response.data)
        self.assertTrue(response.data['cover'].endswith('.jpg'))
