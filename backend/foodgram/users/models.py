from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    """Модель юзер"""
    email = models.EmailField(
        max_length=254,
        unique=True,
        validators=[EmailValidator, ],
        verbose_name='электронная почта'
    )
    first_name = models.TextField(
        max_length=150,
        verbose_name='имя',
    )
    last_name = models.TextField(
        max_length=150,
        verbose_name='фамилия'
    )
    is_subscribed = models.BooleanField(blank=True, default=False)

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
        related_name='subscription',
        verbose_name='автор',
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.CheckConstraint(
                check=~Q(author=F('follower')), name='author_not_user'),
            models.UniqueConstraint(
                fields=['follower', 'author'], name='unique_follow')]
