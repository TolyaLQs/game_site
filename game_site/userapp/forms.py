# userapp/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Форма для создания нового пользователя с email и username.
    Расширяет стандартную форму UserCreationForm.
    """
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    class Meta:
        model = User
        fields = ('email', 'username')
        field_classes = {}


class CustomUserChangeForm(UserChangeForm):
    """
    Форма для обновления информации о пользователе в админке.
    """
    password = None  # Убираем поле пароля

    class Meta:
        model = User
        fields = ('email', 'username', 'avatar', 'bio', 'is_active', 'is_staff')


class UserRegisterForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Форма для обновления информации о пользователе.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'avatar', 'bio', 'is_active', 'is_staff')

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['avatar'].widget.attrs['class'] = 'form-control'
        self.fields['bio'].widget.attrs['class'] = 'form-control'
        self.fields['is_active'].widget.attrs['class'] = 'form-control'
        self.fields['is_staff'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super(UserUpdateForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """
    Форма для обновления информации о профиле пользователя.
    """
    class Meta:
        model = User
        fields = ('avatar', 'bio')

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs['class'] = 'form-control'
        self.fields['bio'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super(ProfileUpdateForm, self).save(commit=False)
        if commit:
            user.save()
        return user