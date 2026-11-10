from django.urls import path
from . import views
app_name = 'donations'
urlpatterns = [
    path('', views.donation_list, name='list'),
    path('export/', views.export_csv, name='export'),
    path('record/<int:response_pk>/', views.record_donation, name='record'),
]
