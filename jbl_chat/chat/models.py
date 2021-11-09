from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

# Create your models here.


class Message(models.Model):
    message = models.TextField(blank=False, null=False)
    sended_by = models.ForeignKey(
        User, related_name='user_sender', null=True, on_delete=models.CASCADE)
    received_by = models.ForeignKey(
        User, related_name='user_receiver', null=True, on_delete=models.CASCADE)
    room = models.CharField(max_length=255)
    send_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('send_at',)

    def __str__(self) -> str:
        return f'Message send by {self.sended_by} and recieved by {self.received_by}'

    def last_messages_room(self, room_name):
        Message.objects.filter(room=room_name).all()

    def fetch_messages(user):
        user_sender = User.objects.filter(username=user)[0]
        if user_sender is None:
            raise Exception(f'User {user} sender not exist')
        return Message.objects.filter(Q(sended_by=user_sender) | Q(received_by=user_sender)).all()

    def save_message(message, sender, receiver, room):
        user_sender = User.objects.filter(username=sender)[0]
        if user_sender is None:
            raise Exception(f'User {sender} sender not exist')
        user_receiver = User.objects.filter(username=receiver)[0]
        if user_receiver is None:
            raise Exception(f'User {receiver} receiver not exist')

        Message.objects.create(
            message=message, sended_by=user_sender, received_by=user_receiver, room=room)


class AppUsersConnected(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="connected")
    connect_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user

    def logged_users():
        return AppUsersConnected.objects.all()
