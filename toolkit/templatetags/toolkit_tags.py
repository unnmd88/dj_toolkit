from django import template
import toolkit.views as views


register = template.Library()

@register.simple_tag()
def get_controller_types():
    return views.controllers_menu


@register.inclusion_tag('toolkit/controller_types.html')
def show_controllers():
    types = views.controllers_menu
    return {'types': types}

