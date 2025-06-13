# userapp/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
import userapp.views as view

name = 'userapp'

urlpatterns = [
    # Регистрация
    path('register/', view.register, name='register'),
    path('login/', view.user_login, name='login'),
    path('logout/', view.user_logout, name='logout'),
    path('register/', view.user_register, name='register'),
    # Вход/выход
    # path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    # Управление профилем
    path('profile/', view.profile, name='profile'),
    path('profile/update/', view.profile_update, name='profile_update'),

    # Смена пароля
    path('password-change/',
         auth_views.PasswordChangeView.as_view(template_name='users/password_change.html'),
         name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),

    # Сброс пароля
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]

