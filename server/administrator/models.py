from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Boolean fields to select the type of account.
    is_admin = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
