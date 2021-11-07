from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def index(request):
    return render(request, 'index.html')


def room(request, room_name):
    return render(request, 'room.html', {'room_name': room_name})

def user_room(request, user_room_name):
    return render(request, 'user_room.html', {'user_room_name': user_room_name})


@csrf_exempt
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            redirect()
    else:
        return render(request, 'login.html')
