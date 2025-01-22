import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.db.models import Sum
import re
from .forms import ReservationForm
import datetime
from django.db import models

from .models import User,Product, Reviews,Sales, SalesItems, Reservation

def index(request):
    average_rating = Reviews.objects.aggregate(Avg('rating'))['rating__avg']
    form = ReservationForm()

    if average_rating is None:
        average_rating = 0

    categories = Product.objects.values_list('category', flat=True).distinct()
    products_by_category = {category: Product.objects.filter(category=category) for category in categories}
    reviews = Reviews.objects.order_by('-date')

    # Fetch most sold items by category
    most_sold_items = {}
    for category in categories:
        # Filter products by category and annotate sales quantity
        products_in_category = Product.objects.filter(category=category).annotate(
            total_quantity=Sum('salesitems__quantity')
        ).order_by('-total_quantity')  # Order by highest quantity sold

        if products_in_category.exists():
            most_sold_items[category] = products_in_category.first()

    return render(request, 'rest_mng/index.html',{
            'products_by_category':products_by_category,
            'reviews': reviews,
            'average_rating': round(average_rating, 2),
            'most_sold_items': most_sold_items,
            'form': form
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, "rest_mng/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "rest_mng/login.html")


def logout_view(request):
    logout(request)
    return redirect('index')

def terms(request):
    return render(request, 'rest_mng/T&Cs.html')


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Password validation regex
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

        # Check if passwords match
        if password != confirmation:
            return render(request, "rest_mng/register.html", {
                "message": "Passwords must match."
            })

        # Check password strength
        if not re.match(password_pattern, password):
            return render(request, "rest_mng/register.html", {
                "message": "Password must be at least 8 characters long, include a number, a special character, "
                           "and have a mix of uppercase and lowercase letters."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "rest_mng/register.html", {
                "message": "Username already taken."
            })

        # Log the user in and redirect to index
        login(request, user)
        return redirect(reverse("index"))

    # If GET request, render the registration page
    return render(request, "rest_mng/register.html")


@login_required
def favorites(request):
    user = request.user  # Get the logged-in user
    favorite_products = Product.objects.filter(favorite=user)
    return render(request, 'rest_mng/favorites.html', {'favorite_products': favorite_products})


def new_product(request):
        if request.method == "POST":
            title = request.POST['prod_name']
            description = request.POST['prod_desc']
            price = request.POST['price']
            category = request.POST['category']
            image = request.FILES.get('image')

            # Save the product
            product = Product(
                prod_name=title,
                prod_desc=description,
                price=price,
                category=category,
                image=image
            )
            product.save()
            messages.success(request, f"New product has been created !!!")
            return redirect('dashboard')

        return render(request, 'index.html')


# Admin dashboard with superuser only restriction
def admin_dashboard(view_func):
    def decorated_view_func(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "This page is only available for users with appropriate clearance level, "
                                    "if you have this clearance please log in with your credentials then try again.")
            return redirect('login')  # Redirect to the login page
        return view_func(request, *args, **kwargs)
    return decorated_view_func


@admin_dashboard
def dashboard(request):
    orders = Sales.objects.prefetch_related('items__product')
    products = Product.objects.all()
    reservations = Reservation.objects.all()

    return render(request, 'rest_mng/admin.html',{
        'orders':orders,
        'products' : products,
        'reservations': reservations
    })

def toggle_stock(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.in_stock = not product.in_stock
        product.save()
        messages.success(request, f"The stock status of {product.prod_name} has been updated.")
    return redirect('dashboard')

def delete_product(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product_name = product.prod_name
        product.delete()
        messages.success(request, f"The product '{product_name}' has been deleted.")
    return redirect('dashboard')

@csrf_exempt
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Sales, id=order_id)
        current_status = order.status

        if current_status == 'Preparing':
            order.status = 'Ready'
        elif current_status == 'Ready':
            order.status = 'Collected'
        else:
            return JsonResponse(
                {'status': 'failed', 'message': f'Order is not in a valid status to update from "{current_status}".'})

        order.save()
        return JsonResponse({'status': 'success', 'new_status': order.status})

    return JsonResponse({'status': 'failed', 'message': 'Invalid request method.'})


# Add Review
def add_review(request):
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '')

        review = Reviews(rating=rating, comment=comment, person = request.user)

        try:
            # Validate model instance
            review.full_clean()  # Triggers validation
            review.save()

            # Add success message
            messages.success(request, "Review added successfully!")
        except ValidationError as e:
            # Add error message
            messages.error(request, f"Failed to add review: {e.message_dict}")

            # Redirect to the index route
        return redirect('index')
@csrf_exempt
def checkout(request):
    if request.method == 'POST':
        cart = json.loads(request.body)
        user = request.user
        total_price = sum(
            Decimal(item['price']) * item['quantity']
            for item in cart.values()
        )

        # Create a new Sale
        sale = Sales.objects.create(user=user, total_price=total_price)

        # Add items to the sale
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            SalesItems.objects.create(
                sale=sale,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )

            # Optionally reduce stock
            # product.stock -= item['quantity']
            product.save()

        return JsonResponse({'message': 'Checkout successful!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def history(request):
    sales = Sales.objects.order_by('-date')
    items = SalesItems.objects.all()
    return render(request, 'rest_mng/sales_history.html',{
        'sales':sales,
        'items': items
    })

@login_required
def toggle_favorite(request):
    if request.method == 'POST':
        product_id = request.POST['product_id']
        product = get_object_or_404(Product, id=product_id)
        user = request.user
        if product in user.favorite.all():
            user.favorite.remove(product)
        else:
            user.favorite.add(product)
    return redirect('index')


# Reservation view
@login_required
def make_reservation(request):
    form = ReservationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        reservation = form.save(commit=False)
        reservation.user = request.user
        reservation.save()
        messages.success(request, "Your reservation has been made!")
        return redirect('index')
    else:
        print('Something went wrong')



@login_required
def available_times(request):
    date = request.GET.get('date')
    if not date:
        return JsonResponse({'times': []})

    try:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'times': []})

    available_times = []
    for hour in range(10, 22):
        time = f"{hour}:00"
        total_reserved = (
            Reservation.objects.filter(date=date_obj, time=time)
            .aggregate(total=models.Sum('num_tables'))['total'] or 0
        )
        if total_reserved < 10:
            available_times.append(time)

    return JsonResponse({'times': available_times})