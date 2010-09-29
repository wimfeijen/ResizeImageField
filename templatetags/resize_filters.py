from django import template

register = template.Library()

from address.resize_image import ORIGINAL_NAME, SCALED_NAME, THUMB_NAME

@register.filter
def scaled(value):
    return value.replace(ORIGINAL_NAME, SCALED_NAME, 1)

@register.filter
def thumb(value):
    return value.replace(ORIGINAL_NAME, THUMB_NAME, 1)
