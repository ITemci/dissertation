from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from django.utils import timezone

class User(AbstractUser):
    pass

class Product(models.Model):
    prod_name = models.CharField(max_length=15)
    prod_desc = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=[('Soft Drink', 'Soft Drink'), ('Alcohol Drink', 'Alcohol Drink'), ('Food', 'Food')], default='N/A')
    date = models.DateTimeField(auto_now_add=True)
    in_stock = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    #favorite = models.ManyToManyField(User, blank= True,  related_name="favorite")
