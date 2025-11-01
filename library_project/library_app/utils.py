from django.core.mail import send_mail


def send_rental_confirmation_email(user, book, due_date):
    """Отправляет пользователю подтверждение аренды книги на электронную почту."""
    subject = "Подтверждение аренды книги"
    message = (
        f"Здравствуйте, {user.username}!\n\n"
        f'Вы взяли в аренду книгу "{book.title}". '
        f"Пожалуйста, верните её до {due_date}."
    )
    send_mail(subject, message, None, [user.email])
