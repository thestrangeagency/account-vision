from django import template

register = template.Library()


@register.inclusion_tag('table.html')
def table(object_list, fields):
    headers = fields.values()
    rows = []
    for obj in object_list:
        cols = []
        for field in fields.keys():
            value = getattr(obj, field)
            if callable(value):
                value = value()
            cols.append(str(value))
        rows.append(cols)
    return {
        'headers': headers,
        'rows': rows,
    }
