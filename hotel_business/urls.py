from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from hotel.views import LoginView, ServicesView, logout_view

# Перенаправление с корня на страницу логина
def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='root'),
    path('login/', LoginView.as_view(), name='login'),
    path('services/', ServicesView.as_view(), name='services'),
    path('logout/', logout_view, name='logout'),
]