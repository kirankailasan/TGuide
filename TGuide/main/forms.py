from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import AuthenticationForm
from .models import PlanTrip
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, help_text="Password should be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one digit.")
    confirm_password = forms.CharField(widget=forms.PasswordInput, help_text="Please re-enter your password.", error_messages={'invalid': 'Passwords do not match.'})


    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            self.add_error('confirm_password', forms.ValidationError('Passwords do not match.'))
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 3 or len(username) > 30:
            raise forms.ValidationError("Username must be between 3 and 30 characters.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Invalid email address.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email address is already in use.")
        return email



class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", max_length=254, widget=forms.EmailInput(attrs={'autofocus': True}))

class PlanTripForm(forms.ModelForm):
    class Meta:
        model = PlanTrip
        fields = ['location', 'budget', 'start_date', 'end_date', 'people', 'preferences']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

