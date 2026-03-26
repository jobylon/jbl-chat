from django.urls import path

from chat.views import (
    login_view,
    UserListView,
    conversation_view,
    SendMessageView,
    poll_messages,
    search_users,
    delete_message,
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("conversation/<int:user_id>/", conversation_view, name="conversation"),
    path("send-message/<int:user_id>/", SendMessageView.as_view(), name="send-message"),
    path("poll-messages/<int:user_id>/", poll_messages, name="poll-messages"),
    path("search-users/", search_users, name="search-users"),
    path("delete-message/<int:message_id>/", delete_message, name="delete-message"),
]
