from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile, Product

class CustomerRegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(max_length=15, required=True)
    image = forms.ImageField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data


class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}))



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'category', 'description', 'image']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError('Price must be greater than zero.')
        return price