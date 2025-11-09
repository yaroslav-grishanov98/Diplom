from django.contrib import admin

from .models import Author, Book, BookIssue


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Админ-класс для модели Author."""

    list_display = ("first_name", "last_name", "birth_date")
    search_fields = ("first_name", "last_name")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Админ-класс для модели Book."""

    list_display = ("title", "genre", "published_date")
    search_fields = ("title", "genre")
    filter_horizontal = ("authors",)


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    """Админ-класс для модели BookIssue."""

    list_display = (
        "book",
        "user",
        "issue_date",
        "due_date",
        "return_date",
        "is_returned",
    )
    list_filter = ("issue_date", "due_date", "return_date")
