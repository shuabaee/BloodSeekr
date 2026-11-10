from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import RegistrationForm

# The form posts "password"/"confirm_password"; Django's UserCreationForm calls them password1/password2.
FIELD_ALIASES = {'password1': 'password', 'password2': 'confirm_password'}


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    submitted = {}
    errors = {}
    if request.method == 'POST':
        data = request.POST.copy()
        data['password1'] = data.get('password', '')
        data['password2'] = data.get('confirm_password', '')
        form = RegistrationForm(data)
        submitted = {key: data.get(key, '') for key in ['first_name', 'last_name', 'username', 'email']}
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect(f"{reverse('login:login')}?registered=1")
        errors = {FIELD_ALIASES.get(name, name): [str(e) for e in items] for name, items in form.errors.items()}
    return render(request, 'register/register.html', {
        'submitted': submitted,
        'errors': errors,
        'error_summary': bool(errors),
    })
