from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=250, required=True)
    last_name = forms.CharField(max_length=250, required=True)
    email = forms.EmailField(
        max_length=250, help_text='e.g. youremail@gmail.com')
    phone_number = forms.CharField(
        validators=[RegexValidator(
            r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        required=True,
        label="Phone Number",
        help_text="Enter phone number in the format: '+999999999'. Up to 15 digits allowed."
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
