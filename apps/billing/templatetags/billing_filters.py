from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Lấy giá trị từ dictionary: dictionary|get_item:key"""
    return dictionary.get(key)