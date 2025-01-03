# Generated by Django 5.1.3 on 2024-12-06 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_mng', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prod_name', models.CharField(max_length=15)),
                ('prod_desc', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('category', models.CharField(choices=[('Soft Drink', 'Soft Drink'), ('Alcohol Drink', 'Alcohol Drink'), ('Food', 'Food')], default='N/A', max_length=50)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('in_stock', models.BooleanField(default=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
            ],
        ),
    ]
