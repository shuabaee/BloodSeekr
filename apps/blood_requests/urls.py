from django.urls import path
from . import views
app_name = 'blood_requests'
urlpatterns = [path('<int:pk>/location/',views.edit_location,name='edit_location'),path('map-data/',views.request_map_data,name='map_data'),path('',views.request_list,name='list'),path('create/',views.create_request,name='create'),path('<int:pk>/',views.request_detail,name='detail'),path('<int:pk>/respond/',views.respond,name='respond'),path('<int:pk>/status/',views.update_status,name='status'),path('<int:pk>/responses/<int:response_pk>/',views.response_action,name='response_action')]
