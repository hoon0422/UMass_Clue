from django.shortcuts import render
import django.contrib.auth.views as authviews


class LoginView(authviews.LoginView):
    template_name = 'accounts/login.html'


class LogoutView(authviews.LogoutView):
    template_name = 'accounts/logout.html'


class PasswordChangeView(authviews.PasswordChangeView):
    template_name = 'accounts/login.html'


class PasswordChangeDoneView(authviews.PasswordChangeDoneView):
    template_name = 'accounts/login.html'


class PasswordResetView(authviews.PasswordResetView):
    template_name = 'accounts/password_reset.html'


class PasswordResetDoneView(authviews.PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class PasswordResetConfirmView(authviews.PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'


class PasswordResetCompleteView(authviews.PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
