from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def index(request):
    if request.user.is_authenticated:
        return render(request, 'index.html', {'username': request.user.username})
    return redirect('login')


def room(request, room_name):
    return render(request, 'room.html', {'room_name': room_name})


def user_room(request, user_room_name):
    return render(request, 'user_room.html', {'user_room_name': user_room_name})


@csrf_exempt
def log_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        return redirect('login')
    else:
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, 'login.html')


@csrf_exempt
def log_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')
