from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from chat.models import Message


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
def login_view(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("/users/")
        except Exception:
            pass

    users = User.objects.all()
    return render(request, "chat/login.html", {"users": users})


# ---------------------------------------------------------------------------
# User list
# ---------------------------------------------------------------------------
class UserListView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/login/")

        all_users = User.objects.all()
        other_users = []
        for u in all_users:
            if u.id != request.user.id:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT COUNT(*) FROM chat_message "
                        "WHERE sender_id = %s AND receiver_id = %s AND status = %s",
                        [u.id, request.user.id, "sent"],
                    )
                    unread_count = cursor.fetchone()[0]

                other_users.append(
                    {
                        "id": u.id,
                        "username": u.username,
                        "email": u.email,
                        "unread": unread_count,
                    }
                )

        return render(
            request,
            "chat/user_list.html",
            {
                "users": other_users,
                "current_user": request.user,
            },
        )


# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------
def conversation_view(request, user_id):
    if not request.user.is_authenticated:
        return redirect("/login/")

    try:
        other_user = User.objects.get(id=user_id)
    except Exception:
        return HttpResponse("User not found", status=404)

    sent_messages = Message.objects.filter(
        sender=request.user,
        receiver__id=user_id,
    )
    received_messages = Message.objects.filter(
        sender__id=user_id,
        receiver=request.user,
    )

    for msg in received_messages:
        if msg.status == "sent" or msg.status == "delivered":
            msg.status = "read"
            msg.save()

    all_messages = list(sent_messages) + list(received_messages)
    all_messages.sort(key=lambda m: m.timestamp)

    formatted_messages = []
    for msg in all_messages:
        formatted_messages.append(
            {
                "id": msg.id,
                "sender": msg.sender.username,
                "receiver": msg.receiver.username,
                "content": mark_safe(msg.content),
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "status": msg.status,
                "is_mine": msg.sender == request.user,
            }
        )

    last_message_id = 0
    for msg in all_messages:
        if msg.id > last_message_id:
            last_message_id = msg.id

    return render(
        request,
        "chat/conversation.html",
        {
            "messages": formatted_messages,
            "other_user": other_user,
            "current_user": request.user,
            "last_message_id": last_message_id,
        },
    )


# ---------------------------------------------------------------------------
# Send message
# ---------------------------------------------------------------------------
class SendMessageView(View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, user_id):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Not authenticated"}, status=401)

        content = request.POST.get("content", "")
        if not content.strip():
            return JsonResponse({"error": "Empty message"}, status=400)

        try:
            receiver = User.objects.get(id=user_id)
        except Exception:
            return JsonResponse({"error": "User not found"}, status=404)

        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            status="sent",
        )

        message_html = (
            '<div class="message message-mine">'
            '  <div class="message-header">'
            f"    <strong>{request.user.username}</strong>"
            f'    <span class="timestamp">{message.timestamp.strftime("%Y-%m-%d %H:%M:%S")}</span>'
            "  </div>"
            f'  <div class="message-body">{mark_safe(message.content)}</div>'
            f'  <div class="message-status">{message.status}</div>'
            "</div>"
        )

        return JsonResponse(
            {
                "success": True,
                "message_id": message.id,
                "html": message_html,
            }
        )


# ---------------------------------------------------------------------------
# Poll for new messages
# ---------------------------------------------------------------------------
@csrf_exempt
def poll_messages(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    last_id = request.GET.get("last_id", 0)
    try:
        last_id = int(last_id)
    except Exception:
        last_id = 0

    new_received = Message.objects.filter(
        sender__id=user_id,
        receiver=request.user,
        id__gt=last_id,
    )

    for msg in new_received:
        if msg.status == "sent" or msg.status == "delivered":
            msg.status = "read"
            msg.save()

    new_sent = Message.objects.filter(
        sender=request.user,
        receiver__id=user_id,
        id__gt=last_id,
    )

    all_new = list(new_received) + list(new_sent)
    all_new.sort(key=lambda m: m.timestamp)

    messages_html = ""
    max_id = last_id
    for msg in all_new:
        is_mine = msg.sender == request.user
        css_class = "message-mine" if is_mine else "message-theirs"
        messages_html += (
            f'<div class="message {css_class}">'
            f'  <div class="message-header">'
            f"    <strong>{msg.sender.username}</strong>"
            f'    <span class="timestamp">{msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")}</span>'
            f"  </div>"
            f'  <div class="message-body">{mark_safe(msg.content)}</div>'
            f'  <div class="message-status">{msg.status}</div>'
            f"</div>"
        )
        if msg.id > max_id:
            max_id = msg.id

    return JsonResponse(
        {
            "html": messages_html,
            "last_id": max_id,
        }
    )


# ---------------------------------------------------------------------------
# Search users
# ---------------------------------------------------------------------------
def search_users(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    query = request.GET.get("q", "")
    all_users = User.objects.all()
    results = []
    for u in all_users:
        if u.id != request.user.id:
            if query.lower() in u.username.lower() or query.lower() in u.email.lower():
                results.append(
                    {
                        "id": u.id,
                        "username": u.username,
                        "email": u.email,
                    }
                )

    html = ""
    for u in results:
        html += (
            f'<a href="/conversation/{u["id"]}/" class="user-card">'
            f'  <div class="user-name">{u["username"]}</div>'
            f'  <div class="user-email">{u["email"]}</div>'
            f"</a>"
        )

    if not html:
        html = '<div class="no-results">No users found</div>'

    return JsonResponse({"html": html})


# ---------------------------------------------------------------------------
# Delete message
# ---------------------------------------------------------------------------
@csrf_exempt
@require_POST
def delete_message(request, message_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    try:
        msg = Message.objects.get(id=message_id)
    except Exception:
        return JsonResponse({"error": "Message not found"}, status=404)

    msg.delete()
    return JsonResponse({"success": True})
