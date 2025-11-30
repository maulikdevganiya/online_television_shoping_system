import re
from django import forms
from .models import UserRegister,Carousel
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

    # Validate Last Name
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

class CarouselForm(forms.ModelForm):
    class Meta:
        model = Carousel
        fields = ['c_title', 'c_link', 'sort_order', 'c_status', 'c_img']