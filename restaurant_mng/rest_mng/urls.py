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
    path("terms", views.terms, name="terms"),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('toggle-stock/<int:product_id>/', views.toggle_stock, name='toggle_stock'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('make-reservation/', views.make_reservation, name='make_reservation'),
    path('available-times/', views.available_times, name='available_times'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)