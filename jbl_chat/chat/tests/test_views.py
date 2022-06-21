from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate
from chat.views import Conversations


class ViewTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="12345")
        self.bob = User.objects.create_user(username="bob", password="12345")
        self.clive = User.objects.create_user(username="clive", password="12345")

    def test_creating_conversation_without_self_is_disallowed(self):
        data = {"participants": [self.bob.id, self.clive.id]}
        factory = APIRequestFactory()
        user = self.alice
        view = Conversations.as_view()

        request = factory.post("/chat/conversations", data, format="json")
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 400)

    def test_creating_conversation_with_self(self):
        data = {"participants": [self.alice.id, self.clive.id]}
        factory = APIRequestFactory()
        user = self.alice
        view = Conversations.as_view()

        request = factory.post("/chat/conversations", data, format="json")
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
