from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservations")
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    num_tables = models.IntegerField(default=1)

    class Meta:
        # Prevent duplicate reservations for same date and time
        unique_together = ('date', 'time')

    def __str__(self):
        return f"Reservation by {self.user} on {self.date} at {self.time}"

    @staticmethod
    def is_available(date, time, num_tables=1):
        total_reserved = (
                Reservation.objects.filter(date=date, time=time)
                .aggregate(total=models.Sum('num_tables'))['total'] or 0
        )
        return total_reserved + num_tables <= 10