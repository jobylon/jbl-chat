from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count

from .models import User, Conversation, Message
from .serializers import ConversationSerializer, UserSerializer, MessageSerializer


class Conversations(APIView):
    def get(self, request):
        conversations = Conversation.objects.filter(participants=request.user)
        serializer = ConversationSerializer(conversations, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        data = JSONParser().parse(request)
        serializer = ConversationSerializer(data=data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = request.user
            if user not in data["participants"]:
                return JsonResponse(
                    {"error": "conversation must include self"}, status=400
                )
            existing_conv = self.get_existing_conversation(data["participants"])
            if existing_conv is not None:
                return JsonResponse(
                    {"error": "conversation exists", "conflicting_id": existing_conv},
                    status=409,
                )
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    def get_existing_conversation(self, participants):
        conversations = Conversation.objects.annotate(
            count=Count("participants")
        ).filter(count=len(participants))
        for p in participants:
            conversations = conversations.filter(participants__pk=p.id)

        if len(conversations) > 0:
            return conversations[0].id


class Users(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)


class Messages(APIView):
    def get(self, request, conversation=None):
        if not conversation:
            return JsonResponse({"error": "invalid conversation id"}, status=400)
        if not Conversation.objects.filter(pk=conversation).filter(
            participants__pk=request.user.id
        ):
            return JsonResponse({"error": "conversation not found"}, status=404)

        messages = Message.objects.filter(conversation__pk=conversation).order_by(
            "timestamp"
        )
        serializer = MessageSerializer(messages, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, conversation=None):

        if not conversation:
            return JsonResponse({"error": "invalid conversation id"}, status=400)
        if not Conversation.objects.filter(pk=conversation).filter(
            participants__pk=request.user.id
        ):
            return JsonResponse({"error": "conversation not found"}, status=404)

        data = JSONParser().parse(request)
        data["conversation"] = conversation
        data["sender"] = request.user.id
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, safe=False)
        else:
            return JsonResponse(serializer.errors, status=400)
