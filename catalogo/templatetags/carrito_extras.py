from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()


@register.filter
def multiplicar(a, b):
    try:
        return Decimal(str(a)) * Decimal(str(b))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")