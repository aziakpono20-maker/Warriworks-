
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class WarriWorksUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError('An email address is required.')

        if not username:
            raise ValueError('A username is required.')

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', 'customer')

        return self._create_user(
            email,
            username,
            password,
            **extra_fields
        )

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields['role'] = 'admin'

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            email,
            username,
            password,
            **extra_fields
        )


class User(AbstractUser):

    password = models.CharField(max_length=255, blank=True)

    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        ARTISAN = 'artisan', 'Artisan'
        ADMIN = 'admin', 'Administrator'

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    phone = models.CharField(max_length=24, blank=True)

    legacy_password_hash = models.CharField(
        max_length=255,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = WarriWorksUserManager()

    def __str__(self):
        return self.email
