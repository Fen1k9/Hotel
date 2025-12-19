from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
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

    search = request.GET.get('search', '')
    if search:
        services = services.filter(name__icontains=search)

    # Получаем скидку клиента
    client_discount = 0
    if request.user.is_authenticated and request.user.role == 'client':
        try:
            if hasattr(request.user, 'guest_profile') and request.user.guest_profile:
                client_discount = float(request.user.guest_profile.discount)
            else:
                guest = Guest.objects.filter(user=request.user).first()
                if guest:
                    client_discount = float(guest.discount)
        except:
            client_discount = 0

    # Рассчитываем данные для каждого сервиса
    services_data = []
    for service in services:
        original_price = float(service.price)

        # Рассчитываем цену со скидкой
        if client_discount > 0:
            discounted_price = original_price * (1 - client_discount / 100)
            discounted_price_formatted = f"{discounted_price:.2f}"
        else:
            discounted_price_formatted = f"{original_price:.2f}"

        service_info = {
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'price': f"{original_price:.2f}",
            'discounted_price': discounted_price_formatted,
            'is_available': service.is_available,
            'has_discount': client_discount > 0,
            'client_discount': client_discount,
            'highlight': client_discount > 10  # Подсветка при скидке >10%
        }

        services_data.append(service_info)

    return render(request, 'services.html', {
        'services': services_data,
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

    # Исправленная сортировка
    sort_order = request.GET.get('sort', 'asc')

    if sort_order == 'desc':
        clients = Guest.objects.all().order_by('-full_name')  # Я-А
    else:
        clients = Guest.objects.all().order_by('full_name')  # А-Я (по умолчанию)

    return render(request, 'clients.html', {
        'clients': clients,
        'sort_order': sort_order
    })


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

    # Уникальные значения спальных мест
    bed_counts = Room.objects.values_list('bed_count', flat=True).distinct().order_by('bed_count')

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

        try:
            booking = Booking.objects.get(booking_id=booking_id)
            service = Service.objects.get(id=service_id)

            service_provision = ServiceProvision(
                booking=booking,
                service=service,
                quantity=quantity,
                provision_date=provision_date
            )
            service_provision.save()

            # УСПЕШНОЕ УВЕДОМЛЕНИЕ
            messages.success(request,
                             f'Услуга "{service.name}" успешно добавлена для клиента {booking.guest.full_name}!')

            return redirect('book_service')

        except Booking.DoesNotExist:
            messages.error(request, 'Ошибка: бронирование не найдено')
        except Service.DoesNotExist:
            messages.error(request, 'Ошибка: услуга не найдена')
        except Exception as e:
            messages.error(request, f'Ошибка при записи: {str(e)}')

    bookings = Booking.objects.all()
    services = Service.objects.all()

    return render(request, 'book_service.html', {
        'bookings': bookings,
        'services': services
    })