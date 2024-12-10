from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_product", views.new_product, name="new_product"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("add_review", views.add_review, name="add_review"),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)