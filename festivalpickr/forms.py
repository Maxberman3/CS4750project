from .models import User
from django import forms
from localflavor.us.forms import USZipCodeField, USStateSelect, USStateField
from festivalpickr.utils import has_name_chars

from django.forms import ModelForm
# from django_coinpayments.models import Payment
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):

    first_name = forms.CharField(max_length=40, required=True, help_text='Required')
    last_name = forms.CharField(max_length=40, required=True, help_text='Required')
    email = forms.EmailField(max_length=254, required=True, help_text='Required')
    address = forms.CharField(max_length=254, required=True, help_text='Required')
    state = USStateField(required=True, widget=USStateSelect(), help_text='Required')
    city = forms.CharField(max_length=85, required=True, help_text='Required')
    zip_code = USZipCodeField(required=True, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2','first_name',
                  'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        has_name_chars(first_name)
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        has_name_chars(last_name)
        return last_name

    def clean_city(self):
        city=self.cleaned_data['city']
        has_name_chars(city)
        return city

    def clean_address(self):
        address=self.cleaned_data['address']
        for char in address:
            if char in "!@$%^&*()~,./?;:":
                raise forms.ValidationError('You included an in Invalid Symbol in the address field')
        return address
# FORM CLASS TO HANDLE BITCOIN PAYMENTS
# class PaymentForm(ModelForm):
#
#     email = forms.EmailField(max_length=254, required=True, help_text='Required')
#
#     class Meta:
#         model = Payment
#         fields = ['email', 'currency_paid']
