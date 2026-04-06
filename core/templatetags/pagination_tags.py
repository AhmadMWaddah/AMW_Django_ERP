"""Custom template tags for pagination and query parameter handling."""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def preserve_query_params(context, **kwargs):
    """
    Return a query string preserving all current GET params plus any new ones.

    Usage:
        {% preserve_query_params page=2 %}
        {% preserve_query_params page=page_obj.next_page_number %}
    """
    request = context.get("request")
    if not request:
        return ""

    query_params = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            query_params[key] = str(value)

    if query_params:
        return f"?{query_params.urlencode()}"
    return ""
