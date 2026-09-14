from django.contrib.auth.models import AbstractUser
from django.db import models


class AppUser(AbstractUser):
    """
    The singular authentication engine for the entire ecosystem.
    Only holds global system credentials. App-specific traits belong
    in their respective application Profile modules.
    """
    email = models.EmailField()

    def __str__(self):
        return self.username
