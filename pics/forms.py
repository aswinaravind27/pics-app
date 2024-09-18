from django.forms import ModelForm
from . models import Customers,Albums,Photo
from django import forms

class UsersLoginForm(ModelForm):
    password = forms.CharField(
        label='Password',  # Custom label
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'id': 'exampleFormControlTextarea1', 
            'placeholder': 'Enter your password', 
            'required': True
        })
    )
    email = forms.EmailField(
        label='Email ID',  # Custom label
        max_length=200, 
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'id': 'exampleFormControlTextarea1', 
            'placeholder': 'Enter your email', 
            'required': True
        })
    )

    class Meta: 
        model = Customers
        fields = ['email', 'password'] 

class SignupForm(ModelForm):
    class Meta:
        model = Customers
        fields = '__all__'

class AlbumCreations(ModelForm):

    class Meta:
        model = Albums
        fields = ['name','share']

class ImagesForm(forms.Form):
    from django import forms

class ImagesForm(forms.Form):
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        label='Upload Images',
        required=False
    )
