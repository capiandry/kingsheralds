from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('products/', views.products, name='products'),
    path('spices/', views.spices_view, name='spices'),
    path('herbs/', views.herbs_view, name='herbs'),
    path('pdfs/', views.pdfs_view, name='pdfs'),
    path('unlock-pdf/', views.unlock_pdf, name='unlock_pdf'),
    path('download-pdf/<int:product_id>/', views.download_pdf, name='download_pdf'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('founder/', views.founder_view, name='founder'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
]