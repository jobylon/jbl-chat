from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_recieved')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
