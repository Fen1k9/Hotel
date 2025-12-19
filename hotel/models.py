from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('client', 'Клиент'),
        ('guest', 'Гость'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='guest'
    )

class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    series = models.CharField(max_length=20, verbose_name="Серия")
    number = models.CharField(max_length=50, verbose_name="Номер")
    issue_date = models.DateField(verbose_name="Дата выдачи")
    issued_by = models.CharField(max_length=255, verbose_name="Кем выдан")

    def __str__(self):
        return f"{self.series} {self.number}"


class Guest(models.Model):
    guest_id = models.AutoField(primary_key=True, verbose_name="ГостьИД")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    birth_date = models.DateField(verbose_name="Дата рождения")
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        verbose_name="Документ",
        related_name="guests"
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="Скидка (%)"
    )
    # Оставить только здесь связь
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='guest_profile',
        verbose_name="Пользователь"
    )

    def __str__(self):
        return self.full_name


    def get_user(self):
        return self.user


class Category(models.Model):
    category_id = models.AutoField(primary_key=True, verbose_name="КатегорииИД")
    name = models.CharField(max_length=100, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name


class Item(models.Model):
    item_id = models.AutoField(primary_key=True, verbose_name="ПредметИД")
    name = models.CharField(max_length=100, verbose_name="Название")

    def __str__(self):
        return self.name


class Equipment(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name="Предмет"
    )

    def __str__(self):
        return f"{self.category.name} - {self.item.name}"


class Room(models.Model):
    room_id = models.AutoField(primary_key=True, verbose_name="НомерИД")
    floor = models.IntegerField(verbose_name="Этаж")
    room_count = models.IntegerField(verbose_name="Количество комнат")
    bed_count = models.IntegerField(verbose_name="Количество спальных мест")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория",
        related_name="rooms"
    )

    def __str__(self):
        return f"Номер {self.room_id} ({self.category.name})"


class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True, verbose_name="БроныИД")
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        verbose_name="Гость",
        related_name="bookings"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        verbose_name="Номер",
        related_name="bookings"
    )
    check_in_date = models.DateField(verbose_name="Дата заезда")
    check_out_date = models.DateField(verbose_name="Дата выезда")
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость"
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="ОплаченоФакт"
    )

    def __str__(self):
        return f"Бронирование {self.booking_id} - {self.guest.full_name}"


class ServiceProvision(models.Model):
    provision_id = models.AutoField(primary_key=True, verbose_name="УИД")
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        verbose_name="Бронирование",
        related_name="service_provisions"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name="Услуга"
    )
    quantity = models.IntegerField(default=1, verbose_name="Количество")
    provision_date = models.DateField(verbose_name="Дата оказания услуги")

    def __str__(self):
        return f"{self.service.name} для {self.booking.guest.full_name}"