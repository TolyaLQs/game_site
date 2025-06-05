from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
# from .forms import CreateUserForm
from .models import User, Notification, Comment
from django.db.models.signals import post_save
from django.views.decorators.cache import cache_page
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_welcome_email(user_id):
    user = User.objects.get(id=user_id)
    send_mail(
        'Добро пожаловать на GameSite!',
        f'Привет, {user.username}! Спасибо за регистрацию.',
        'noreply@gamesite.com',
        [user.email],
        fail_silently=False,
    )


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} успешно создан! Теперь вы можете войти.')
            send_welcome_email.delay(user.id)
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@receiver(post_save, sender=Comment)
def notify_about_comment(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.content_object.author,
            message=f"Новый комментарий к вашему посту '{instance.content_object.title[:30]}...'",
            link=instance.get_absolute_url()
        )


@login_required
def profile(request):
    return render(request, 'users/profile.html')


@login_required
def profile_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'users/profile_update.html', context)


def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('user:profile', kwargs={'username': request.user.username}))
    else:
        if request.method == 'POST':
            try:
                try:
                    username = User.objects.get(email=request.POST['username']).username()
                except:
                    username = User.objects.get(username=request.POST['username']).username()
                password = request.POST.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect(reverse('main:index'))
                else:
                    error = 'Не правильно введены данные.'
                    context = {
                        'error': error,
                    }
                    return render(request, 'user/login.html', context)
            except User.DoesNotExist:
                request.session['username'] = request.POST.get('username')
                return HttpResponseRedirect(reverse('user:register'))

        return render(request, 'user/login.html')


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('user:login'))


def user_register(request):
    username = request.session.get('username', 'Нет имя')
    label_name = 'Hi! ' + username
    error = None
    if request.method == 'POST':
        register_form = UserRegisterForm(request.POST, request.FILES)
        if register_form.is_valid():
            register_form.save()
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('user:profile'))
            else:
                error = 'Не правильно введены данные.'
                context = {
                    'error': error,
                }
        else:
            error = 'Ошибка'
            register_form = UserRegisterForm(request.POST if request.POST else None)
            for reg in register_form:
                if reg.name == 'username':
                    reg.initial = username
                    label_name = 'Hi! ' + username
    else:
        register_form = UserRegisterForm()
        for reg in register_form:
            if reg.name == 'username':
                reg.initial = username
                label_name = 'Hi! ' + username
    context = {
        'register_form': register_form,
        'label_name': label_name,
        'error': error,
        'username': username
    }

    return render(request, 'user/register.html', {'register_form': register_form,
                                                  'label_name': label_name, 'error': error})


@cache_page(60 * 15)  # Кэшировать на 15 минут
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'userapp/profile.html', {'user': user})

