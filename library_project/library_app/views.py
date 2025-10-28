from rest_framework import viewsets, generics, filters, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth.models import User
from .models import Author, Book, BookIssue
from .serializers import (
    AuthorSerializer, BookSerializer, UserSerializer,
    RegisterSerializer, BookIssueSerializer
)
from rest_framework.response import Response
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin, IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['first_name', 'last_name', 'birth_date']
    search_fields = ['first_name', 'last_name']


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().prefetch_related('authors')
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['genre', 'published_date', 'authors__first_name', 'authors__last_name']
    search_fields = ['title', 'genre', 'authors__first_name', 'authors__last_name']


class BookIssueViewSet(viewsets.ModelViewSet):
    serializer_class = BookIssueSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return BookIssue.objects.all()
        return BookIssue.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


def book_list(request):
    books = Book.objects.all().prefetch_related('authors')
    return render(request, 'library_app/book_list.html', {'books': books})
