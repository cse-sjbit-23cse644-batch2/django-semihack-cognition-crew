"""
Custom template filters and tags for form rendering with Bootstrap 5
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def add_class(field, css_class):
    """Add CSS class to form field"""
    if hasattr(field, 'field'):
        # Get the rendered field HTML
        field_html = str(field)
        # Add class to the first input, select, or textarea element
        if '<select' in field_html:
            field_html = field_html.replace('<select', f'<select class="{css_class}"', 1)
        elif '<textarea' in field_html:
            field_html = field_html.replace('<textarea', f'<textarea class="{css_class}"', 1)
        elif '<input' in field_html:
            field_html = field_html.replace('<input', f'<input class="{css_class}"', 1)
        return mark_safe(field_html)
    return field
