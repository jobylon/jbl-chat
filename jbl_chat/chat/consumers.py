import json

from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope["user"]
        print(self.user)
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print('Websocket disconnected: ' + str(close_code))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        pass

    async def receive(self, text_data):
        json_message = json.loads(text_data)
        message = json_message['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class UserChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(self.scope['url_route']['kwargs'])
        self.room_name = self.scope['url_route']['kwargs']['user_room_name']
        print(self.scope['url_route']['kwargs'])
        self.user = self.scope["user"]
        print(self.user)
        self.room_group_name = 'chat_%s' % self.user
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print('Websocket disconnected: ' + str(close_code))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        pass

    async def receive(self, text_data):
        json_message = json.loads(text_data)
        message = json_message['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

        # Send message to room group
        await self.channel_layer.group_send(
            'chat_%s' % self.room_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
