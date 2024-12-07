import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User,Product

# Create your views here.
def index(request):
    products = Product.objects.all()
    return render(request, 'rest_mng/index.html',{
        'products':products
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