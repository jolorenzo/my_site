from django import template

register = template.Library()


@register.filter(name='quantity_is_correct')
def quantity_is_correct(total_quantity, quantity_by_box=50):
    return (total_quantity % quantity_by_box) == 0
