from django.contrib.auth.models import User
from django.db import models


class Conversation(models.Model):
    participants = models.ManyToManyField(User)


class Message(models.Model):

    sender = models.ForeignKey(User, models.SET_NULL, related_name="+", null=True)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    conversation = models.ForeignKey(
        Conversation, models.CASCADE, related_name="messages"
    )
