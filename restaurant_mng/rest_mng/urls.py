from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("favorites", views.favorites, name="favorites"),
    path("new_product", views.new_product, name="new_product"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("add_review", views.add_review, name="add_review"),
    path("checkout", views.checkout, name="checkout"),
    path("history", views.history, name="history"),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)