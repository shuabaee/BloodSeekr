"""Small presentation helpers shared by every feature template."""
import datetime as dt

from django import template
from django.templatetags.static import static
from django.utils import timezone
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def icon(name, size=18, css=""):
    """Render an icon from the shared SVG sprite: {% icon 'home' %}."""
    return format_html(
        '<svg class="icon {}" width="{}" height="{}" style="width:{}rem;height:{}rem" aria-hidden="true" focusable="false">'
        '<use href="{}#{}"></use></svg>',
        css, size, size, round(float(size) / 16, 4), round(float(size) / 16, 4), static("images/shared/icons.svg"), name,
    )


STATUS_LABELS = {
    "in_progress": "In progress", "blood_center": "Blood center", "routine": "Routine",
}


@register.filter
def label(value):
    """'in_progress' -> 'In progress'."""
    value = str(value or "")
    return STATUS_LABELS.get(value) or value.replace("_", " ").capitalize()


@register.filter
def days_until(value):
    """Human wording for a due date: 'Today', 'Tomorrow', 'In 5 days', '3 days overdue'."""
    if not isinstance(value, dt.date):
        return ""
    delta = (value - timezone.localdate()).days
    if delta == 0:
        return "Needed today"
    if delta == 1:
        return "Needed tomorrow"
    if delta > 1:
        return f"In {delta} days"
    return f"{-delta} day{'s' if delta != -1 else ''} overdue"


@register.filter
def due_class(value):
    """CSS modifier for how soon a date is: 'is-today', 'is-soon' or ''."""
    if not isinstance(value, dt.date):
        return ""
    delta = (value - timezone.localdate()).days
    return "is-today" if delta <= 0 else "is-soon" if delta <= 2 else ""


@register.filter
def initial(user):
    name = getattr(user, "first_name", "") or getattr(user, "username", "") or "U"
    return name[:1].upper()


@register.filter
def message_icon(tag):
    return {"success": "check-circle", "error": "alert", "warning": "alert"}.get(str(tag).split()[-1], "info")
