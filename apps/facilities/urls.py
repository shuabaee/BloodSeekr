from django.urls import path
from . import views
app_name = 'facilities'
urlpatterns = [path('options/',views.facility_options,name='options'),path('add/',views.manage_facility,name='add'),path('<int:pk>/edit/',views.manage_facility,name='edit'),path('',views.facility_list,name='list'),path('<int:pk>/',views.facility_detail,name='detail')]
