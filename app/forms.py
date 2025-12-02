import re
from django import forms
from .models import UserRegister, Address, Carousel
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = UserRegister
        fields = ['name', 'last_name', 'email', 'password']

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if not name:
            raise forms.ValidationError("This field is required.")

        if not re.match(r'^[A-Za-z ]+$', name):
            raise forms.ValidationError("First Name must contain only letters.")

        return name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')

        if not last_name:
            raise forms.ValidationError("This field is required.")

        if not re.match(r'^[A-Za-z ]+$', last_name):
            raise forms.ValidationError("Last Name must contain only letters.")

        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if UserRegister.objects.filter(email=email).exists():
            raise ValidationError("Email already exists!")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirm_password")

        if p1 and p2 and p1 != p2:
            self.add_error("confirm_password", "Passwords do not match!")

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserRegister
        fields = ['name', 'last_name', 'email', 'date_of_birth', 'gender', 'mobile_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Enter your last name'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Enter your email'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'gender': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'mobile_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Enter your mobile number'}),
        }

class CarouselForm(forms.ModelForm):
    class Meta:
        model = Carousel
        fields = ['c_title', 'c_link', 'sort_order', 'c_status', 'c_img']
        widgets = {
            'c_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter carousel title'}),
            'c_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter link URL'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter sort order'}),
            'c_status': forms.Select(attrs={'class': 'form-control'}),
            'c_img': forms.FileInput(attrs={'class': 'form-control'}),
        }

# Other forms can be added here if needed
