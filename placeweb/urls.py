"""placeweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
import os.path

from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from . import views
from .settings import BASE_DIR, MEDIA_ROOT

urlpatterns = [  # pylint: disable=invalid-name
    path('', views.index, name='index'),
    path('submit/', views.submit, name='submit'),
    path('status/', views.status, name='status'),
    path('history/', views.history, name='history'),
    path('delete/', views.delete, name='delete'),
    path('download/<str:location>', views.download, name='download'),
    re_path(r'^figures/tmp/(?P<path>.*)$',
            serve, {
                'document_root': os.path.join(
                    MEDIA_ROOT,
                    'figures/tmp')
            }),
    re_path(r'^documentation/(?P<path>.*)$',
            serve, {
                'document_root': os.path.join(
                    BASE_DIR,
                    'placeweb/static/placeweb/documentation')
            }),
    path('admin/', admin.site.urls),
]
