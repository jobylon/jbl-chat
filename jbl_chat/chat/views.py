from chat.models import User, Message
from chat.serializers import UserSerializer, MessageSerializer
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'head']

class MessageViewSet(ModelViewSet):
    serializer_class = MessageSerializer
    http_method_names = ['get', 'post', 'head']
    def perform_create(self, serializer):
        recipient = User.objects.get(pk=self.kwargs['user_pk'])
        serializer.save(sender=self.request.user, recipient=recipient)
    def get_queryset(self):
        return (Message.objects.filter(Q(sender=self.kwargs['user_pk']) & Q(recipient=self.request.user.id)
                                      | Q(sender=self.request.user.id) & Q(recipient=self.kwargs['user_pk']))
                               .order_by('created_at'))
