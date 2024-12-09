from django.db import models
from django.contrib.auth.models import (
    PermissionsMixin,
    AbstractBaseUser,
    BaseUserManager,
)
from django.conf import settings
from cryptography.fernet import Fernet
import base64

ENCRYPTION_KEY = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode())
cipher_suite = Fernet(ENCRYPTION_KEY)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self) -> str:
        return self.email


class GoogleSheetToken(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="google_sheet_token"
    )
    encrypted_access_token = models.CharField(max_length=255)
    encrypted_refresh_token = models.CharField(max_length=255)

    def set_access_token(self, token):
        self.encrypted_access_token = cipher_suite.encrypt(token.encode()).decode()

    def get_access_token(self):
        return cipher_suite.decrypt(self.encrypted_access_token.encode()).decode()

    def set_refresh_token(self, token):
        self.encrypted_refresh_token = cipher_suite.encrypt(token.encode()).decode()

    def get_refresh_token(self):
        return cipher_suite.decrypt(self.encrypted_refresh_token.encode()).decode()


class OAuthSession(models.Model):
    session_state = models.CharField(max_length=255)
