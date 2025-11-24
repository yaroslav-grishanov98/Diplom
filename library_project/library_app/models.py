from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg


class Author(models.Model):
    """
    Модель автора книги.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(
        upload_to="authors/photos/", null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def average_rating(self):
        ratings = Rating.objects.filter(book__authors=self)
        if ratings.exists():
            return ratings.aggregate(models.Avg("score"))["score__avg"]
        return None


class Book(models.Model):
    """
    Модель книги.
    """

    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author, related_name="books")
    genre = models.CharField(max_length=100, blank=True)
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to="books/covers/", null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        result = self.ratings.aggregate(Avg("score"))
        return result["score__avg"] or 0


class BookIssue(models.Model):
    """
    Модель выдачи книги пользователю.
    """

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="issues")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="issued_books"
    )
    issue_date = models.DateField(auto_now_add=True)
    rental_period = models.PositiveIntegerField(default=14)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    @property
    def is_returned(self):
        return self.return_date is not None

    def __str__(self):
        return f"{self.book.title} issued to {self.user.username}"


class Rating(models.Model):
    """
    Модель рейтинга книги.
    """

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ratings")
    score = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("book", "user")

    def __str__(self):
        return f"{self.user.username} rated {self.book.title} as {self.score}"


class Comment(models.Model):
    """
    Модель комментария к книге.
    """

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.book.title}"
