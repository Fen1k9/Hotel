from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from .models import Service, User, Guest, Booking, ServiceProvision, Category, Room


def login_view(request):
    if request.user.is_authenticated:
        return redirect('services')

    if request.method == 'POST':
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

    return render(request, 'login.html')


def services_view(request):
    services = Service.objects.all()

    search = request.GET.get('search')
    if search:
        services = services.filter(name__icontains=search)

    # Получаем скидку клиента если он авторизован
    client_discount = 0
    if request.user.is_authenticated and request.user.role == 'client':
        try:
            guest = Guest.objects.get(guest_id=request.user.username)
            client_discount = guest.discount
        except:
            client_discount = 0

    return render(request, 'services.html', {
        'services': services,
        'is_guest': not request.user.is_authenticated,
        'client_discount': client_discount,
        'search': search
    })


def logout_view(request):
    logout(request)
    return redirect('login')


def clients_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role not in ['manager', 'admin']:
        return render(request, 'clients.html', {'error': 'Доступ запрещен'})

    clients = Guest.objects.all()
    return render(request, 'clients.html', {'clients': clients})


def rooms_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    rooms = Room.objects.all()

    bed_count = request.GET.get('bed_count')
    if bed_count:
        rooms = rooms.filter(bed_count=bed_count)

    category_id = request.GET.get('category')
    if category_id:
        rooms = rooms.filter(category_id=category_id)

    categories = Category.objects.all()

    all_rooms = Room.objects.all()
    bed_counts = []
    for room in all_rooms:
        if room.bed_count not in bed_counts:
            bed_counts.append(room.bed_count)
    bed_counts.sort()

    return render(request, 'rooms.html', {
        'rooms': rooms,
        'categories': categories,
        'bed_counts': bed_counts,
        'current_bed_count': bed_count,
        'current_category': category_id
    })


def book_service_view(request):
    if not request.user.is_authenticated or request.user.role not in ['manager', 'admin']:
        return redirect('login')

    if request.method == 'POST':
        booking_id = request.POST.get('booking')
        service_id = request.POST.get('service')
        quantity = request.POST.get('quantity', 1)
        provision_date = request.POST.get('provision_date')

        booking = Booking.objects.get(booking_id=booking_id)
        service = Service.objects.get(id=service_id)

        service_provision = ServiceProvision(
            booking=booking,
            service=service,
            quantity=quantity,
            provision_date=provision_date
        )
        service_provision.save()

        return render(request, 'book_service.html', {
            'bookings': Booking.objects.all(),
            'services': Service.objects.all(),
            'success': f'Услуга "{service.name}" добавлена для клиента {booking.guest.full_name}'
        })

    bookings = Booking.objects.all()
    services = Service.objects.all()

    return render(request, 'book_service.html', {
        'bookings': bookings,
        'services': services
    })