from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views import View
from django.contrib.auth.hashers import make_password
from .models import Service, User


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('services')
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        # Регистрация
        if 'register' in request.POST:
            if User.objects.filter(username=username).exists():
                return render(request, 'login.html', {'error': 'Логин уже занят'})

            user = User(username=username, role='client')
            user.password = make_password(password)
            user.save()
            login(request, user)
            return redirect('services')

        # Вход
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('services')
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})


class ServicesView(View):
    def get(self, request):
        services = Service.objects.all()
        return render(request, 'services.html', {
            'services': services,
            'is_guest': not request.user.is_authenticated
        })


def logout_view(request):
    logout(request)
    return redirect('login')