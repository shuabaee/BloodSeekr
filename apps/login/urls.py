from django.urls import path

from . import views

app_name = "login"

urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot/", views.ForgotPasswordView.as_view(), name="password_reset"),
    path("forgot/sent/", views.ForgotPasswordDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.ResetPasswordConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", views.ResetPasswordCompleteView.as_view(), name="password_reset_complete"),
]
