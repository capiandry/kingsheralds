from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
import json
import os
from datetime import datetime  # moved import to top

from .models import Product, PDFUnlock, UserProfile
from .forms import RegisterForm, ProductForm
from .decorators import admin_required


def home(request):
    featured_products = Product.objects.filter(is_available=True)[:3]
    return render(request, 'home.html', {'featured_products': featured_products})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({'success': True, 'redirect': '/products/'})
        return JsonResponse({'success': False, 'error': 'Invalid credentials'})
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def products(request):
    search_query = request.GET.get('search', '')
    if search_query:
        products_list = Product.objects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query),
            is_available=True
        )
    else:
        products_list = Product.objects.filter(is_available=True)
    
    spices = products_list.filter(category='spice')
    herbs = products_list.filter(category='herb')
    pdfs = products_list.filter(category='pdf')
    
    # Get suggestions for search (up to 10)
    suggestions = list(Product.objects.filter(is_available=True).values('name', 'category')[:10])
    
    return render(request, 'products.html', {
        'spices': spices[:3],
        'herbs': herbs[:3],
        'pdfs': pdfs[:3],
        'all_spices': spices,
        'all_herbs': herbs,
        'all_pdfs': pdfs,
        'search_query': search_query,
        'suggestions': suggestions,
    })


def spices_view(request):
    spices = Product.objects.filter(category='spice', is_available=True)
    return render(request, 'spices.html', {'products': spices, 'category': 'Spices'})


def herbs_view(request):
    herbs = Product.objects.filter(category='herb', is_available=True)
    return render(request, 'herbs.html', {'products': herbs, 'category': 'Herbs'})


def pdfs_view(request):
    pdf_products = Product.objects.filter(category='pdf', is_available=True)
    unlocked_pdfs = []
    if request.user.is_authenticated:
        unlocked_pdfs = PDFUnlock.objects.filter(user=request.user).values_list('product_id', flat=True)
    
    for pdf in pdf_products:
        pdf.is_unlocked = pdf.id in unlocked_pdfs
    
    return render(request, 'pdfs.html', {'products': pdf_products, 'category': 'Health PDFs'})


@login_required
@csrf_exempt
def unlock_pdf(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            mpesa_number = data.get('mpesa_number')
            
            if not product_id:
                return JsonResponse({'success': False, 'error': 'Product ID missing'}, status=400)
            
            product = get_object_or_404(Product, id=product_id, category='pdf')
            
            # Check if already unlocked
            if PDFUnlock.objects.filter(user=request.user, product=product).exists():
                return JsonResponse({'success': True, 'already_unlocked': True, 'download_url': f'/download-pdf/{product.id}/'})
            
            # Simulate M-Pesa payment verification
            # In production, replace with actual M-Pesa API call
            # For demo, we assume payment is successful
            transaction_id = f"SIM{product_id}{request.user.id}{datetime.now().timestamp()}"
            
            # Create unlock record
            PDFUnlock.objects.create(
                user=request.user,
                product=product,
                mpesa_transaction_id=transaction_id
            )
            
            return JsonResponse({
                'success': True,
                'download_url': f'/download-pdf/{product.id}/'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def download_pdf(request, product_id):
    product = get_object_or_404(Product, id=product_id, category='pdf')
    
    # Check if user has unlocked this PDF
    if not PDFUnlock.objects.filter(user=request.user, product=product).exists():
        return HttpResponseForbidden("You haven't unlocked this PDF.")
    
    if product.pdf_file and product.pdf_file.path and os.path.exists(product.pdf_file.path):
        with open(product.pdf_file.path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{product.name}.pdf"'
            return response
    
    return HttpResponse("PDF file not found.", status=404)


@admin_required
def admin_dashboard(request):
    users = UserProfile.objects.select_related('user').all()
    products = Product.objects.all().order_by('-created_at')
    form = ProductForm()
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('admin_dashboard')
    
    return render(request, 'admin.html', {
        'users': users,
        'products': products,
        'form': form,
    })


@admin_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'admin_edit_product.html', {'form': form, 'product': product})


@admin_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)


def terms_view(request):
    return render(request, 'terms.html')


def privacy_view(request):
    return render(request, 'privacy.html')


def founder_view(request):
    return render(request, 'founder.html')


def search_suggestions(request):
    query = request.GET.get('q', '').strip()
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_available=True
        )[:5]
        suggestions = [{'name': p.name, 'category': p.get_category_display()} for p in products]
        return JsonResponse({'suggestions': suggestions})
    return JsonResponse({'suggestions': []})