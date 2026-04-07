"""Custom template filters for rendering audit log data."""

import json
from decimal import Decimal

from django import template
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="render_audit_data")
def render_audit_data(data):
    """
    Render audit data (before_data, after_data, extra_data) in a human-readable format.

    Handles:
    - None values
    - Dictionaries
    - Lists
    - Decimal values
    - JSON strings
    - Scalar values

    Usage:
        {{ log.before_data|render_audit_data }}

    Security: All values are escaped using conditional_escape() to prevent XSS.
    """
    if data is None:
        return format_html('<span class="u-text-muted">{}</span>', "No data")

    # If it's a string, try to parse as JSON
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except (json.JSONDecodeError, ValueError):
            # Not JSON, escape and display as text
            return format_html('<span class="u-text-sm">{}</span>', conditional_escape(data))

    # Render the data as HTML
    return _render_value(data, indent_level=0)


def _render_value(value, indent_level=0):
    """Recursively render a value as HTML, escaping all user-controlled data."""
    if value is None:
        return format_html('<span class="u-text-muted">{}</span>', "None")

    if isinstance(value, Decimal):
        return format_html("<code>{}</code>", conditional_escape(str(value)))

    if isinstance(value, bool):
        label = "True" if value else "False"
        badge_class = "badge--success" if value else "badge--danger"
        return format_html('<span class="badge {}">{}</span>', badge_class, conditional_escape(label))

    if isinstance(value, (int, float)):
        return format_html('<span class="u-font-semibold">{}</span>', conditional_escape(str(value)))

    if isinstance(value, str):
        # Check if it looks like a datetime
        if "T" in value and ("Z" in value or "+" in value):
            return format_html('<span class="u-text-muted">{}</span>', conditional_escape(value))
        # ESCAPE all string values to prevent XSS
        return format_html("<span>{}</span>", conditional_escape(value))

    if isinstance(value, dict):
        return _render_dict(value, indent_level)

    if isinstance(value, (list, tuple)):
        return _render_list(value, indent_level)

    # Fallback: escape anything we don't explicitly handle
    return format_html("<span>{}</span>", conditional_escape(str(value)))


def _render_dict(data, indent_level):
    """Render a dictionary as a nested HTML structure with escaped values."""
    if not data:
        return format_html('<span class="u-text-muted">{}</span>', "{}")

    parts = []
    for key, value in data.items():
        # Keys are from our code, but escape them anyway for safety
        key_html = conditional_escape(str(key))
        value_html = _render_value(value, indent_level + 1)

        parts.append(
            format_html(
                '<div style="margin-bottom: 8px;">'
                '<div style="margin-bottom: 4px;">'
                '<code style="font-size: var(--font-size-xs, 0.75rem); color: var(--color-text-muted, #64748b);">{}:</code>'
                "</div>"
                "{}"
                "</div>",
                key_html,
                value_html,
            )
        )

    # Join all parts and wrap in container
    inner = mark_safe("".join(str(p) for p in parts))
    return format_html(
        '<div style="margin-left: 12px; border-left: 2px solid var(--color-border, #e2e8f0); padding-left: 12px;">{}</div>',
        inner,
    )


def _render_list(data, indent_level):
    """Render a list as a structured HTML list with escaped values."""
    if not data:
        return format_html('<span class="u-text-muted">{}</span>', "[]")

    parts = []
    for item in data:
        item_html = _render_value(item, indent_level + 1)
        parts.append(format_html('<li style="margin-bottom: 4px;">{}</li>', item_html))

    inner = mark_safe("".join(str(p) for p in parts))
    return format_html('<ul style="margin-left: 16px; list-style-type: disc;">{}</ul>', inner)
