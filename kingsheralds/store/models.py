from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('spice', 'Spice'),
        ('herb', 'Herb'),
        ('pdf', 'Health PDF'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight_grams = models.CharField(max_length=50, blank=True, help_text="e.g., 200/250 grams")
    unit = models.CharField(max_length=20, blank=True, default='g', help_text="e.g., g, mg, ml, piece, capsule")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class PDFUnlock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, limit_choices_to={'category': 'pdf'})
    unlocked_at = models.DateTimeField(auto_now_add=True)
    mpesa_transaction_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ['user', 'product']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    official_names = models.CharField(max_length=200)
    
    def __str__(self):
        return self.user.username