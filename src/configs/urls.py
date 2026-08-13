"""
URL configuration for configs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, register_converter

from api.converters import APIVersionConverter
from utils.views import healthz

register_converter(APIVersionConverter, "api_version")

urlpatterns = [
    path("api/<api_version:version>/", include("api.urls")),
    path("auth/", include("mozilla_django_oidc.urls")),
    path("healthz/", healthz, name="healthz"),
    path("i18n/", include("django.conf.urls.i18n")),
    path('tinymce/', include('tinymce.urls')),
]

# Language prefix in URL
urlpatterns += i18n_patterns(
    path("", include("django_epfl_entra_id.urls")),
    path("", include("homepages.urls")),
    path("", include("news.urls")),
    path("admin/", admin.site.urls),
)


if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()


# Custom Error Handlers
# https://github.com/epfl-si/django-epfl-web2018#readme

handler400 = "django_epfl_web2018.views.error_400"
handler403 = "django_epfl_web2018.views.error_403"
handler404 = "django_epfl_web2018.views.error_404"
handler500 = "django_epfl_web2018.views.error_500"
