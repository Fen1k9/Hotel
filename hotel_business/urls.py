from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from hotel import views

# Перенаправление с корня на страницу логина
def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='root'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('logout/', views.logout_view, name='logout'),
    path('clients/', views.ClientsView.as_view(), name='clients'),
    ]