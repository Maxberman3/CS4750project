from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from localflavor.us.forms import USZipCodeField, USStateSelect, USStateField

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
