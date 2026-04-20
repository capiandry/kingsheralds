from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, UserProfile

class RegisterForm(UserCreationForm):
    official_names = forms.CharField(max_length=200, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                official_names=self.cleaned_data['official_names'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'weight_grams', 'unit', 'image', 'pdf_file', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter product description...'}),
            'unit': forms.TextInput(attrs={'placeholder': 'e.g., g, mg, ml, piece'}),
        }
        help_texts = {
            'unit': 'Specify the unit of measurement (g, mg, ml, piece, capsule, etc.)',
        }