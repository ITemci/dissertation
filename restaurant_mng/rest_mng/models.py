from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from django.utils import timezone

class User(AbstractUser):
    pass

class Product(models.Model):
    prod_name = models.CharField(max_length=15)
    prod_desc = models.CharField(max_length=255)
    price = models.IntegerField()
    category = models.CharField(max_length=15, default="N/A")
    date = models.DateTimeField(auto_now_add=True)
    in_stock = models.BooleanField(default=True)
    image = models.CharField(max_length=255, blank=True)
    favorite = models.ManyToManyField(User, blank= True, null= True, related_name="favorite")
