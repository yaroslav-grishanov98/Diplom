from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Author, Book, BookIssue, Comment, Rating


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Author"""

    class Meta:
        model = Author
        fields = "__all__"


class BookSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Book."""

    author_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Author.objects.all(), write_only=True, source="authors"
    )
    authors = AuthorSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "authors",
            "author_ids",
            "genre",
            "published_date",
            "description",
            "cover",
        ]


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User"""

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class BookIssueSerializer(serializers.ModelSerializer):
    """Сериализатор для модели BookIssue."""

    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source="book", write_only=True
    )
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True, required=False
    )

    class Meta:
        model = BookIssue
        fields = [
            "id",
            "book",
            "book_id",
            "user",
            "user_id",
            "issue_date",
            "due_date",
            "return_date",
            "is_returned",
        ]
        read_only_fields = ["issue_date", "is_returned"]


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    user = serializers.ReadOnlyField(source="user.username")
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Comment
        fields = ["id", "book", "user", "text", "created_at"]


class RatingSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Rating."""

    user = serializers.ReadOnlyField(source="user.username")
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Rating
        fields = ["id", "book", "user", "score", "review", "created_at"]

    def validate_score(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Оценка должна быть от 1 до 5.")
        return value

    def validate(self, data):
        user = self.context["request"].user
        book = data.get("book")
        if Rating.objects.filter(user=user, book=book).exists():
            raise serializers.ValidationError("Вы уже оценили эту книгу.")
        return data
