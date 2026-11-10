from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    error_message = None
    next_url = request.POST.get('next', request.GET.get('next', ''))
    username = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        user = authenticate(request, username=username, password=request.POST.get('password', ''))
        if user is not None:
            login(request, user)
            if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
                next_url = reverse('home:home')
            return redirect(next_url or reverse('home:home'))
        error_message = 'Invalid username or password.'
    return render(request, 'login/login.html', {
        'error_message': error_message,
        'registration_success': request.GET.get('registered') == '1',
        'password_changed': request.GET.get('reset') == '1',
        'next_url': next_url,
        'username': username,
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect('login:login')


# --- Forgot password: Django's built-in flow, with templates owned by this feature ---
class ForgotPasswordView(auth_views.PasswordResetView):
    template_name = 'login/password_reset.html'
    email_template_name = 'login/password_reset_email.txt'
    subject_template_name = 'login/password_reset_subject.txt'
    success_url = reverse_lazy('login:password_reset_done')


class ForgotPasswordDoneView(auth_views.PasswordResetDoneView):
    template_name = 'login/password_reset_done.html'


class ResetPasswordConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'login/password_reset_confirm.html'
    success_url = reverse_lazy('login:password_reset_complete')


class ResetPasswordCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'login/password_reset_complete.html'
