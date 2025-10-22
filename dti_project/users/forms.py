from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django import forms
from .models import User


class AddStaffForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'default_address', 'default_phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}),
            'default_address': forms.TextInput(attrs={'placeholder': 'Address', 'class': 'form-control'}),
            'default_phone': forms.TextInput(attrs={'placeholder': 'Contact Number', 'class': 'form-control'}),
        }


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")  # override 'username' field to be an EmailField

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_('Invalid email or password'))
        return self.cleaned_data


    def get_user(self):
        return getattr(self, 'user_cache', None)

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    default_phone = forms.CharField(required=True, label="Phone Number")
    default_address = forms.CharField(required=True, label="Address")

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'default_phone',
            'default_address',
            'password1',
            'password2',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.default_phone = self.cleaned_data['default_phone']
        user.default_address = self.cleaned_data['default_address']
        user.role == 'business_owner'

        # Generate unique username
        base_username = slugify(f"{user.first_name}.{user.last_name}")
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username

        if commit:
            user.save()
        return user
