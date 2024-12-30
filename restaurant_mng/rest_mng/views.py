import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.db.models import Sum

from .models import User,Product, Reviews,Sales, SalesItems

# Create your views here.
def index(request):
    average_rating = Reviews.objects.aggregate(Avg('rating'))['rating__avg']
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
            'most_sold_items': most_sold_items
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


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "rest_mng/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "rest_mng/register.html", {
                "message": "Username already taken."

            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "rest_mng/register.html")

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
            return redirect('index')

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
    orders = Sales.objects.prefetch_related('items__product').filter(status='Preparing')

    return render(request, 'rest_mng/admin.html',{
        'orders':orders
    })


def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Sales, id=order_id)

        if order.status == 'Preparing':
            order.status = 'Ready'
            order.save()
            return JsonResponse({'status': 'success', 'new_status': order.status})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Order is not in "Preparing" status.'})
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

def history(request):
    sales = Sales.objects.order_by('-date')
    items = SalesItems.objects.all()
    return render(request, 'rest_mng/sales_history.html',{
        'sales':sales,
        'items': items
    })

def add_favorite(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        current_user = request.user

        if current_user in product.favorite.all():
            messages.warning(request, "You have already added this product to favorites.")
        else:
            product.favorite.add(current_user)
            messages.success(request, "Product added to favorites!")

        return redirect('index')
    else:
        messages.error(request, "Invalid request.")
        return redirect('index')

def remove_favorite(request):
    pass