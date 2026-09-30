from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    email = models.EmailField(
        unique=True,
        verbose_name="email address",
        
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="phone number"
    )

    bio = models.TextField(
        blank=True,
        default="",
        verbose_name="biography"
    )

    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username or self.email