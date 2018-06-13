from django import template

register = template.Library()


@register.inclusion_tag('table.html')
def table(object_list, fields):
    headers = []
    for field in fields:
        headers.append(field['name'])
    rows = []
    for obj in object_list:
        cols = []
        for field in fields:
            value = getattr(obj, field['field'])
            if callable(value):
                value = value()
            if 'link' in field:
                url = getattr(obj, field['link'], None)
                if callable(url):
                    url = url()
                cols.append({
                    'url': url,
                    'name': value,
                })
            else:
                cols.append(str(value))
        rows.append(cols)
    return {
        'headers': headers,
        'rows': rows,
    }
