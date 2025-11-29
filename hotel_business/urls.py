from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from hotel import views

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='root'),
    path('login/', views.login_view, name='login'),
    path('services/', views.services_view, name='services'),
    path('logout/', views.logout_view, name='logout'),
    path('clients/', views.clients_view, name='clients'),
    path('rooms/', views.rooms_view, name='rooms'),
    path('book-service/', views.book_service_view, name='book_service'),

]