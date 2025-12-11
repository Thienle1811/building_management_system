from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Lấy giá trị từ dictionary bằng key: {{ mydict|get_item:key }}"""
    if dictionary:
        return dictionary.get(key)
    return None