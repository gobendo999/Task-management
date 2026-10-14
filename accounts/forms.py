import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Profile

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    """
    Registration form with strict email validation, uniqueness check,
    and styled form controls with padding for icons and visibility toggles.
    """
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'Valid email address is strictly required.',
            'invalid': 'Please enter a valid email address (e.g. name@example.com).',
        },
        widget=forms.EmailInput(attrs={
            'class': 'w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 text-sm',
            'placeholder': 'name@example.com',
            'autocomplete': 'email',
            'required': 'required',
        })
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 text-sm',
            'placeholder': 'First Name',
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 text-sm',
            'placeholder': 'Last Name',
            'autocomplete': 'family-name',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configure username widget styling
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({
                'class': 'w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 text-sm',
                'placeholder': 'Choose a unique username',
                'autocomplete': 'username',
            })
        
        # Configure password fields styling with right padding for eye icon toggle
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({
                'class': 'w-full pl-11 pr-11 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 text-sm',
                'placeholder': 'Create strong password',
                'autocomplete': 'new-password',
            })
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'class': 'w-full pl-11 pr-11 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 text-sm',
                'placeholder': 'Re-enter your password',
                'autocomplete': 'new-password',
            })

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('Valid email address is strictly required.')

        # Standard email validator
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Please provide a valid email address (e.g. name@example.com).')

        # Domain structure validation
        if '@' not in email:
            raise ValidationError('Invalid email format.')
        domain = email.split('@')[-1]
        if '.' not in domain or len(domain.split('.')[-1]) < 2:
            raise ValidationError('Please enter an email with a valid domain (e.g., gmail.com, yahoo.com).')

        # Unique email constraint
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists. Please sign in instead.')

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """
    Login form with styled inputs and space for icons and password show/hide toggle.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 text-sm',
            'placeholder': 'Enter your username',
            'autofocus': True,
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full pl-11 pr-11 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 text-sm',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating basic user information with email validation.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 transition text-sm'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 transition text-sm'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 transition text-sm'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError('Email address cannot be empty.')
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Please enter a valid email address.')

        if '@' not in email:
            raise ValidationError('Invalid email address.')
        domain = email.split('@')[-1]
        if '.' not in domain or len(domain.split('.')[-1]) < 2:
            raise ValidationError('Email domain must be valid.')

        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This email address is already in use by another account.')
        return email


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating supplementary profile info.
    """
    class Meta:
        model = Profile
        fields = ['bio', 'phone', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 transition resize-y text-sm',
                'placeholder': 'Tell us something about yourself...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 transition text-sm',
                'placeholder': '+880 1XXXXXXXXX'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 transition text-sm',
                'placeholder': 'City, Country'
            }),
        }
