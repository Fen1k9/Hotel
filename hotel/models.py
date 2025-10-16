from django.db import models
from django.contrib.auth.models import Usergo

class Document(models.Model):
    """
    В данном классе  храненятся документы гостей
    Что есть: серия, номер, дата выдачи и кем выдан документ
    """
    series = models.CharField(max_length=20, verbose_name="Серия")
    number = models.CharField(max_length=50, verbose_name="Номер")
    issue_date = models.DateField(verbose_name="Дата выдачи")
    issued_by = models.CharField(max_length=255, verbose_name="Кем выдан")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return f"{self.series} {self.number}"


class Guest(models.Model):
    """
    Класс гостя отеля
    Что имеется: персональные данные гостя, ссылка на документ и информацию о скидках
    """
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

    class Meta:
        verbose_name = "Гость"
        verbose_name_plural = "Гости"

    def __str__(self):
        return self.full_name


class Category(models.Model):
    """
    В данном классе -  категории номеров
    Определяет характеристики и цену категории номеров
    Определяют цену категории номеров, а также их хара-ри (номеров)
    """
    category_id = models.AutoField(primary_key=True, verbose_name="КатегорииИД")
    name = models.CharField(max_length=100, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Item(models.Model):
    """
    Класс предметов оснащения номеров
    Хранит в себе названия предметов, которые могут быть в номерах
    """
    item_id = models.AutoField(primary_key=True, verbose_name="ПредметИД")
    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return self.name


class Equipment(models.Model):
    """
    Класс для связи категорий и предметов оснащения
    Определяет, какие предметы входят в оснащение каждой категории
    """
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

    class Meta:
        verbose_name = "Оснащение"
        verbose_name_plural = "Оснащение"
        unique_together = ('category', 'item')

    def __str__(self):
        return f"{self.category.name} - {self.item.name}"


class Room(models.Model):
    """
    Класс номера в отеле
    Содержит информацию о номере, его расположении, кол-ве комнат и спальным мест
    Класс связан  с категорией для определения хара-к """

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

    class Meta:
        verbose_name = "Номер"
        verbose_name_plural = "Номера"

    def __str__(self):
        return f"Номер {self.room_id} ({self.category.name})"


class Service(models.Model):
    """
    Класс  услуг, которые может оказать отель
    Содержит информацию об услугах, их стоимости и описании"""

    service_id = models.AutoField(primary_key=True, verbose_name="УслугаИД")
    name = models.CharField(max_length=100, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.name



class Booking(models.Model):
    """
    Класс бронирования номера
    Содержит такую информацию о бронировании, как - гость, номер, даты, стоимость и статус оплаты  """

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

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"Бронирование {self.booking_id} - {self.guest.full_name}"


class ServiceProvision(models.Model):
    """
    Класс об оказании услуг гостям
    Связывает бронирование с оказанными услугами, учитывает кол-во и дату оказания
    """
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

    class Meta:
        verbose_name = "Оказание услуги"
        verbose_name_plural = "Оказание услуг"

    def __str__(self):
        return f"{self.service.name} для {self.booking.guest.full_name}"
