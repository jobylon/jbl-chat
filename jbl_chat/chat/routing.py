from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/room/(?P<room_name>\w+)/$',
            consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/user/(?P<user_room_name>\w+)/$',
            consumers.UserChatConsumer.as_asgi()),
    re_path(r'ws/chat/', consumers.AppChatConsumer.as_asgi()),
]
