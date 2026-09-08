from django import template, utils

register = template.Library()


@register.filter
def label_for(obj):
    return obj.get_label(utils.translation.get_language())
