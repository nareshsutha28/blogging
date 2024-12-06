from django.db import models
from django.contrib.auth.models import AbstractUser
from user.managers import CustomUserManager


# Create your models here.
class User(AbstractUser):

    # Field declarations
    username = None
    email = models.EmailField(unique = True)
    dob = models.DateField(null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
      return "{}".format(self.email)
