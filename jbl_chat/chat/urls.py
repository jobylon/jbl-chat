from django.urls import path
from . import views

urlpatterns = [
    path("conversations/<int:conversation>/messages", views.Messages.as_view()),
    path("conversations", views.Conversations.as_view()),
    path("users", views.Users.as_view()),
]
