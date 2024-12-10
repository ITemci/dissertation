from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
from django.utils import timezone

class User(AbstractUser):
    pass

class Product(models.Model):
    prod_name = models.CharField(max_length=15)
    prod_desc = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=[('Soft Drink', 'Soft Drink'), ('Alcohol Drink', 'Alcohol Drink'), ('Food', 'Food'),('Desert', 'Desert')], default='N/A')
    date = models.DateTimeField(auto_now_add=True)
    in_stock = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    favorite = models.ManyToManyField(User, blank= True,  related_name="favorite")

class Reviews(models.Model):
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )
    person = models.ForeignKey(User, on_delete = models.CASCADE, blank=True, null=True, related_name="person")
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)

class Sales(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales")
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        ('Preparing', 'Preparing'),
        ('Ready', 'Ready'),
        ('Collected', 'Collected'),
    ]
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='Preparing')

class SalesItems(models.Model):
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
