from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import UserProfile

INPUT_CLASS = 'w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-brick-500 text-white placeholder-slate-500'


class CustomAuthenticationForm(AuthenticationForm):
    """Login form with styled inputs."""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': INPUT_CLASS,
        'placeholder': 'Username',
        'autocomplete': 'username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': INPUT_CLASS,
        'placeholder': 'Password',
        'autocomplete': 'current-password',
    }))


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Email', 'autocomplete': 'email'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Username', 'autocomplete': 'username'}),
            'password1': forms.PasswordInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Password', 'autocomplete': 'new-password'}),
            'password2': forms.PasswordInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Confirm password', 'autocomplete': 'new-password'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'notification_frequency']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': INPUT_CLASS,
                'placeholder': 'Tell us about yourself...',
                'rows': 4,
            }),
            'notification_frequency': forms.Select(attrs={'class': INPUT_CLASS}),
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': INPUT_CLASS}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
        }


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['notification_frequency']
        widgets = {'notification_frequency': forms.RadioSelect()}
