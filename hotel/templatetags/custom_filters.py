from django import template

register = template.Library()


@register.filter
def apply_discount(price, discount):
    """Применяет скидку к цене"""
    try:
        # Преобразуем в числа
        price_float = float(price)
        discount_float = float(discount)

        # Рассчитываем новую цену
        discounted_price = price_float * (1 - discount_float / 100)

        # Округляем до 2 знаков после запятой
        return f"{discounted_price:.2f}"
    except (ValueError, TypeError):
        # Если что-то пошло не так, возвращаем исходную цену
        return price