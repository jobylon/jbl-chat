from django.contrib.auth import login
from django.urls import path

from . import views


urlpatterns = [
    path('',views.index, name='index'),
    path('login/', views.log_in, name='login'),
    path('logout/', views.log_out, name='logout'),
    path('room/<str:room_name>/', views.room, name='room'),
    path('user/<str:user_room_name>/', views.user_room, name='user_room'),
]