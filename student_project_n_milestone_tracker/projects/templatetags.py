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
        # ModelChoiceField or similar
        if field.field.widget.__class__.__name__ in ['Select', 'ModelChoiceField']:
            return mark_safe(f'{field} '.replace('<select', f'<select class="{css_class}"'))
        elif field.field.widget.__class__.__name__ == 'Textarea':
            return mark_safe(f'{field}'.replace('<textarea', f'<textarea class="{css_class}"'))
        elif field.field.widget.__class__.__name__ == 'TextInput':
            return mark_safe(f'{field}'.replace('<input', f'<input class="{css_class}"'))
        elif field.field.widget.__class__.__name__ == 'FileInput':
            return mark_safe(f'{field}'.replace('<input', f'<input class="{css_class}"'))
    return field


@register.filter
def add_attrs(field, attrs_str):
    """Add multiple attributes to a form field"""
    attrs = {}
    for attr in attrs_str.split('|'):
        key, value = attr.split(':')
        attrs[key.strip()] = value.strip()

    if hasattr(field, 'field'):
        field.field.widget.attrs.update(attrs)

    return field


@register.inclusion_tag('form_field.html')
def render_form_field(field, css_class='form-control', label_class='form-label'):
    """Render a single form field with Bootstrap styling"""
    return {
        'field': field,
        'css_class': css_class,
        'label_class': label_class,
    }
