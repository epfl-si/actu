from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.pagination import PageNumberPagination


class NewsPagination(PageNumberPagination):
    """Pagination class for the news endpoint."""

    page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", 10)
    page_size_query_param = "limit"
    max_page_size = 100
    page_size_query_description = _(
        "Number of results to return per page. "
        "Defaults to the API page size."
    )
