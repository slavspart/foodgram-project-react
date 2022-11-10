from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db import models
from django.db.models import Q, F


class User(AbstractUser):
    """Модель юзер"""
# поля пароль и username уже есть в Abstractuser
    email = models.EmailField(
        max_length=254,
        unique=True,
        validators=[EmailValidator, ],
    )
    first_name = models.TextField(
        max_length=150,
    )
    last_name = models.TextField(
        max_length=150,
    )
    is_surbscribed = models.BooleanField(blank=True, default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_username_email'
            ),
        ]


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(author=F('follower')), name='author_not_user'),
            models.UniqueConstraint(
                fields=['follower', 'author'], name='unique_follow')]
