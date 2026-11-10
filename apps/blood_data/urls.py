from django.urls import path

from . import views

app_name = "blood_data"

urlpatterns = [
    path("", views.guide, name="guide"),
]
