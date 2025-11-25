from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.views import View
from django.contrib.auth.hashers import make_password
from .models import Service, User, Guest


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('services')
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if 'register' in request.POST:
            if User.objects.filter(username=username).exists():
                return render(request, 'login.html', {'error': 'Логин уже занят'})

            user = User(username=username, role='client')
            user.password = make_password(password)
            user.save()
            login(request, user)
            return redirect('services')
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('services')
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})


class ServicesView(View):
    def get(self, request):
        services = Service.objects.all()
        search_query = request.GET.get('search', '')
        if search_query:
            services = services.filter(name__icontains=search_query)

        return render(request, 'services.html', {
            'services': services,
            'is_guest': not request.user.is_authenticated,
            'search_query': search_query
        })
class ClientsView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.role not in ['manager', 'admin']:
            return render(request, 'clients.html',
                          {'error': 'Доступ запрещен. Только для менеджеров и администраторов.'})
        clients = Guest.objects.all()

        return render(request, 'clients.html', {'clients': clients})

def logout_view(request):
    logout(request)
    return redirect('login')