from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Profile


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
        fields = ['first_name', 'last_name',
                  'username', 'password1', 'password2', 'email', 'phone_number']


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Hypothetical 'editable' parameter controlling field state;
        # you need to pass it when initializing the form
        editable = kwargs.pop('editable', True)
        super(ProfileForm, self).__init__(*args, **kwargs)

        if not editable:
            for field in self.fields.values():
                field.widget.attrs['disabled'] = 'disabled'

    class Meta:
        model = Profile
        fields = ['address_street', 'address_houseNo', 'address_city',
                  'address_postcode', 'address_country', 'birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address_street': forms.TextInput(attrs={'class': 'form-control'}),
            'address_houseNo': forms.TextInput(attrs={'class': 'form-control'}),
            'address_postcode': forms.TextInput(attrs={'class': 'form-control'}),
            'address_city': forms.TextInput(attrs={'class': 'form-control'}),
            'address_country': forms.TextInput(attrs={'class': 'form-control'}),

        }
        # Add any other fields you want the user to be able to edit


# class SignUpForm(UserCreationForm):
#     first_name = forms.CharField(max_length=250, required=True)
#     last_name = forms.CharField(max_length=250, required=True)
#     email = forms.EmailField(
#         max_length=250, help_text='e.g. youremail@gmail.com')
#     phone_number = forms.CharField(validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
#                                    required=True, label="Phone Number", help_text="Enter phone number in the format: '+999999999'. Up to 15 digits allowed.")

#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'username',
#                   'phone_number', 'password1', 'password2']

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.username = self.cleaned_data['username']
#         if commit:
#             user.save()
#         return user

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Name'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}))
    subject = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'placeholder': 'Message', 'rows': '4'}))
