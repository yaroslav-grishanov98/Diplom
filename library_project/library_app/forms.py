from django import forms

from .models import Author, Book


class BookForm(forms.ModelForm):
    """Форма для создания и редактирования модели Book."""

    class Meta:
        model = Book
        fields = [
            "title",
            "authors",
            "genre",
            "published_date",
            "description",
            "cover",
        ]


class AuthorForm(forms.ModelForm):
    """Форма для создания и редактирования модели Author."""

    class Meta:
        model = Author
        fields = [
            "first_name",
            "last_name",
            "birth_date",
            "photo",
        ]
