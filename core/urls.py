# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),                # Django admin route
    path("", include("apps.authentication.urls")),  # Auth routes - login / register
    path("home/", include("apps.home.urls")),       # UI Kits Html files
    path("insert/", include("apps.insert.urls")),
    path("viewer/", include("apps.viewer.urls")),
    path("table/", include("apps.table.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
