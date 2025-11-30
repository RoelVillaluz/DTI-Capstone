import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from datetime import date
from .models import User


# -------------------------------
# ✅ Base class for shared fields
# -------------------------------
class BaseUserForm(forms.ModelForm):
    """Base class for user forms with shared fields and validation."""

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "First Name",
            "class": "form-control",
            "oninput": "this.value=this.value.replace(/[^A-Za-zÀ-ÖØ-öø-ÿ' -]/g,'')",
            "pattern": "[A-Za-zÀ-ÖØ-öø-ÿ' -]+",
            "title": "Letters, spaces, hyphens, and apostrophes only",
        })
    )

    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Last Name",
            "class": "form-control",
            "oninput": "this.value=this.value.replace(/[^A-Za-zÀ-ÖØ-öø-ÿ' -]/g,'')",
            "pattern": "[A-Za-zÀ-ÖØ-öø-ÿ' -]+",
            "title": "Letters, spaces, hyphens, and apostrophes only",
        })
    )

    default_phone = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Contact Number",
            "class": "form-control",
            "type": "tel",
            "pattern": r"\d{11}",
            "maxlength": "11",
            "inputmode": "numeric",
            "oninput": "this.value = this.value.replace(/\\D/g, '').slice(0, 11);"
        })
    )

    default_address = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Address",
            "class": "form-control"
        })
    )

    class Meta:
        abstract = True
        model = User
        fields = ['first_name', 'last_name', 'default_address', 'default_phone']

    # --- Shared validation ---
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '')
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ' -]+", first_name):
            raise forms.ValidationError(
                "First name must contain only letters, spaces, hyphens, or apostrophes."
            )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '')
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ' -]+", last_name):
            raise forms.ValidationError(
                "Last name must contain only letters, spaces, hyphens, or apostrophes."
            )
        return last_name

    def clean_default_phone(self):
        phone = self.cleaned_data.get('default_phone', '')
        if not phone.isdigit() or len(phone) != 11:
            raise forms.ValidationError("Phone number must be exactly 11 digits.")
        return phone


# ----------------------------------------------------
# ❌ Old AddStaffForm (invalid & duplicated definition)
# ----------------------------------------------------
# Commented out because it caused syntax errors and conflicts
# class AddStaffForm(forms.ModelForm):
#     birthday = forms.DateField(
#         required=True,
#         widget=forms.DateInput(attrs={
#             'type': 'date',
#             'class': 'form-control',
#         }),
#         label="Birthday"
#     )
#     ...
# This was redundant and malformed (kept only for reference)


# ---------------------------------
# ✅ Correct AddStaffForm definition
# ---------------------------------
class AddStaffForm(BaseUserForm):
    birthday = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': date.today().replace(year=date.today().year - 15).isoformat(),
        })
    )

    class Meta(BaseUserForm.Meta):
        fields = BaseUserForm.Meta.fields + ['birthday']


# ------------------------------
# ✅ Forgot/Reset Password Forms
# ------------------------------
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")


# --------------------------
# ✅ Custom Login Form
# --------------------------
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


# -------------------------------
# ✅ Custom User Creation Form
# -------------------------------
class CustomUserCreationForm(UserCreationForm, BaseUserForm):
    email = forms.EmailField(required=True)
    default_phone = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(BaseUserForm.Meta):
        model = User
        fields = BaseUserForm.Meta.fields + [
            'email', 'password1', 'password2', 'default_phone', 'first_name', 'last_name'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].validators.append(self.validate_email_format)
        self.fields['default_phone'].validators.append(self.validate_mobile_number)
        self.fields['first_name'].validators.append(self.validate_name)
        self.fields['last_name'].validators.append(self.validate_name)

    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    @classmethod
    def validate_email_format(cls, value):
        pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.fullmatch(pattern, value):
            raise forms.ValidationError("Enter a valid email address.")

    @classmethod
    def validate_mobile_number(cls, value):
        value = str(value)
        if not re.fullmatch(r'09\d{9}', value):
            raise forms.ValidationError("Mobile number must be 11 digits and start with 09.")
        if value == value[0] * 11:
            raise forms.ValidationError("This is not a valid mobile number.")
        pattern = value[:3]
        if pattern * 3 + value[-2:] == value:
            raise forms.ValidationError("This is not a valid mobile number.")

    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ' -]+", value):
            raise forms.ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes.")
        letters_only = re.sub(r"[^A-Za-z]", "", value)
        if len(letters_only) < 2:
            raise forms.ValidationError("Name must have at least 2 letters.")
        seqs = re.findall(r"([a-zA-Z]{3,})", value.lower())
        for seq in seqs:
            if seq * 2 in value.lower():
                raise forms.ValidationError("Name seems invalid or gibberish.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.default_phone = self.cleaned_data['default_phone']
        user.default_address = self.cleaned_data['default_address']
        user.role = 'unverified_owner'

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

# -----------------------------
# ✅ Profile Edit Form
# -----------------------------
class ProfileEditForm(forms.ModelForm):
    birthday = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'max': date.today().replace(year=date.today().year - 15).isoformat(),
            }
        ),
        label="Birthday"
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'profile_picture', 'default_address',
            'default_phone', 'birthday'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'default_address': forms.TextInput(attrs={'class': 'form-control'}),
            'default_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'tel',
                'pattern': r'\d{11}',
                'maxlength': '11',
                'inputmode': 'numeric',
                'oninput': "this.value = this.value.replace(/\\D/g, '').slice(0, 11);"
            }),
        }

    def clean_default_phone(self):
        phone = self.cleaned_data.get('default_phone', '')
        if not phone.isdigit() or len(phone) != 11:
            raise forms.ValidationError("Phone number must be exactly 11 digits.")
        return phone
