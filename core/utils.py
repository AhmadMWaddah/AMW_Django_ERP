"""Core utility functions for the AMW Django ERP project."""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

DEFAULT_PAGE_SIZE = 20


def paginate_queryset(queryset, request, page_size=DEFAULT_PAGE_SIZE):
    """Paginate a queryset with HTMX support.

    Args:
        queryset: The Django QuerySet to paginate.
        request: The HTTP request object (for page number extraction).
        page_size: Number of items per page (default: 20).

    Returns:
        dict: Pagination data including page_obj, has_previous, has_next,
              previous_page_number, next_page_number, total_pages, total_items.
    """
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return {
        "page_obj": page_obj,
        "has_previous": page_obj.has_previous(),
        "has_next": page_obj.has_next(),
        "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
        "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
        "total_pages": paginator.num_pages,
        "total_items": paginator.count,
    }
