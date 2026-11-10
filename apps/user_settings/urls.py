from django.urls import path

from .views import ChangePasswordView, settings_view

app_name = "user_settings"

urlpatterns = [
    path("", settings_view, name="settings"),
    path("password/", ChangePasswordView.as_view(), name="password_change"),
]
