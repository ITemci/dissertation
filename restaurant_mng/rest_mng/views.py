import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from .models import User,Product, Reviews

# Create your views here.
def index(request):
    products = Product.objects.all()
    reviews = Reviews.objects.order_by('-date')
    return render(request, 'rest_mng/index.html',{
        'products':products,
        'reviews': reviews
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
    return render(request, 'rest_mng/admin.html')

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