from django import template

register = template.Library()


@register.inclusion_tag('action.html')
def action(action):
    return {
        'action': action,
    }
