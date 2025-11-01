from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import Group
from rest_framework import viewsets, generics, filters, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import status
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Author, Book, BookIssue, Comment, Rating
from .serializers import (
    AuthorSerializer,
    BookSerializer,
    UserSerializer,
    RegisterSerializer,
    BookIssueSerializer,
    CommentSerializer,
    RatingSerializer,
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin, IsOwnerOrReadOnly
from .forms import BookForm, AuthorForm
from .utils import send_rental_confirmation_email


User = get_user_model()


def visitor_login(request):
    """Обработка входа посетителя по имени."""
    if request.method == "POST":
        username = request.POST.get("username")
        if not username:
            return render(
                request,
                "library_app/visitor_login.html",
                {"error": "Please enter a name"},
            )

        user, created = User.objects.get_or_create(username=username)
        if created:
            visitors_group, _ = Group.objects.get_or_create(name="Visitors")
            user.groups.add(visitors_group)
            user.set_unusable_password()
            user.save()

        login(request, user)
        return redirect("index")

    return render(request, "library_app/visitor_login.html")


class RegisterView(generics.CreateAPIView):
    """API-вью для регистрации пользователей."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class RegisterPageView(APIView):
    """Веб-вью для регистрации через HTML форму."""

    permission_classes = []

    def get(self, request):
        return render(request, "library_app/register.html")

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return redirect("login")
        return render(
            request, "library_app/register.html", {"errors": serializer.errors}
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class AuthorViewSet(viewsets.ModelViewSet):
    """Вьюсет для CRUD операций с авторами."""

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["first_name", "last_name", "birth_date"]
    search_fields = ["first_name", "last_name"]


class BookViewSet(viewsets.ModelViewSet):
    """Вьюсет для CRUD операций с книгами."""

    queryset = Book.objects.all().prefetch_related("authors")
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        "genre",
        "published_date",
        "authors__first_name",
        "authors__last_name",
    ]
    search_fields = ["title", "genre", "authors__first_name", "authors__last_name"]


class BookIssueViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления выдачами книг."""

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
    """Веб-вью для отображения списка книг с поддержкой поиска."""
    query = request.GET.get("search", "")
    if query:
        books = (
            Book.objects.filter(
                Q(title__icontains=query)
                | Q(authors__first_name__icontains=query)
                | Q(authors__last_name__icontains=query)
            )
            .distinct()
            .prefetch_related("authors")
        )
    else:
        books = Book.objects.all().prefetch_related("authors")
    return render(
        request, "library_app/book_list.html", {"books": books, "search": query}
    )


def author_list(request):
    """Веб-вью для отображения списка авторов с поддержкой поиска."""
    query = request.GET.get("search", "")
    if query:
        authors = Author.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).distinct()
    else:
        authors = Author.objects.all()
    return render(
        request, "library_app/author_list.html", {"authors": authors, "search": query}
    )


def index(request):
    """Главная страница сайта."""
    return render(request, "library_app/index.html")


def book_detail(request, pk):
    """Веб-вью для отображения деталей книги, среднего рейтинга и комментариев."""
    book = get_object_or_404(Book, pk=pk)
    average_rating = book.average_rating if hasattr(book, "average_rating") else None
    comments = book.comments.all()
    return render(
        request,
        "library_app/book_detail.html",
        {"book": book, "average_rating": average_rating, "comments": comments},
    )


def author_detail(request, pk):
    """Веб-вью для отображения деталей автора."""
    author = get_object_or_404(Author, pk=pk)
    return render(request, "library_app/author_detail.html", {"author": author})


def is_author(user):
    """Проверяет, принадлежит ли пользователь группе 'Authors'."""
    return user.groups.filter(name="Authors").exists()


@login_required
def book_create(request):
    """Веб-вью для создания новой книги."""
    if not is_author(request.user):
        return redirect("book_list")

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("book_list")
    else:
        form = BookForm()
    return render(request, "library_app/book_form.html", {"form": form})


@login_required
def book_edit(request, pk):
    """Веб-вью для редактирования книги."""
    book = get_object_or_404(Book, pk=pk)
    if not is_author(request.user):
        return redirect("book_detail", pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect("book_detail", pk=pk)
    else:
        form = BookForm(instance=book)
    return render(request, "library_app/book_form.html", {"form": form})


@login_required
def author_create(request):
    """Веб-вью для создания автора."""
    if not is_author(request.user):
        return redirect("author_list")

    if request.method == "POST":
        form = AuthorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("author_list")
    else:
        form = AuthorForm()
    return render(request, "library_app/author_form.html", {"form": form})


@login_required
def author_edit(request, pk):
    """Веб-вью для редактирования автора."""
    author = get_object_or_404(Author, pk=pk)
    if not is_author(request.user):
        return redirect("author_detail", pk=pk)

    if request.method == "POST":
        form = AuthorForm(request.POST, request.FILES, instance=author)
        if form.is_valid():
            form.save()
            return redirect("author_detail", pk=pk)
    else:
        form = AuthorForm(instance=author)
    return render(request, "library_app/author_form.html", {"form": form})


def is_admin(user):
    """Проверяет, является ли пользователь администратором."""
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def book_delete(request, pk):
    """Веб-вью для удаления книги."""
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        book.delete()
        messages.success(request, "Book deleted successfully.")
        return redirect("book_list")

    return render(request, "library_app/book_confirm_delete.html", {"book": book})


@login_required
@user_passes_test(is_admin)
def author_delete(request, pk):
    """Веб-вью для удаления автора."""
    author = get_object_or_404(Author, pk=pk)

    if request.method == "POST":
        author.delete()
        messages.success(request, "Author deleted successfully.")
        return redirect("author_list")

    return render(request, "library_app/author_confirm_delete.html", {"author": author})


class CommentViewSet(viewsets.ModelViewSet):
    """API-вьюсет для комментариев."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RatingViewSet(viewsets.ModelViewSet):
    """API-вьюсет для рейтингов."""

    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@login_required
def add_comment(request, book_id):
    """Веб-вью для добавления комментария к книге."""
    book = get_object_or_404(Book, pk=book_id)
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Comment.objects.create(book=book, user=request.user, text=text)
    return redirect("book_detail", pk=book_id)


@login_required
@require_POST
def book_issue_create(request, book_id):
    """Веб-вью для создания записи о выдаче книги (аренде)."""
    book = get_object_or_404(Book, id=book_id)
    rental_period = int(request.POST.get("rental_period", 14))
    due_date = timezone.now().date() + timezone.timedelta(days=rental_period)
    BookIssue.objects.create(
        book=book, user=request.user, due_date=due_date, rental_period=rental_period
    )
    send_rental_confirmation_email(request.user, book, due_date)
    messages.success(request, f'Вы арендовали книгу "{book.title}" до {due_date}.')
    return redirect("profile")


@login_required
def profile(request):
    """Веб-вью для отображения личного кабинета пользователя с активными арендованными книгами."""
    active_issues = request.user.issued_books.filter(return_date__isnull=True)
    return render(request, "library_app/profile.html", {"active_issues": active_issues})
