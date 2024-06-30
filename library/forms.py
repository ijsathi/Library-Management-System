from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Review, Borrow

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField( required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name','email', 'password1', 'password2')

class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

class ReviewForm(forms.Form):
    rating = forms.IntegerField(min_value=1, max_value=5)
    comment = forms.CharField(widget=forms.Textarea)
    
# class ReviewForm(forms.ModelForm):
#     class Meta:
#         model = Review
#         fields = ['review']

class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = []

class ReturnForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = []
