"""odman URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.static import serve

from odman import settings
from apps.order.views import my_login, my_logout, register, profile, profile_update, profile_confirm,\
    reset_passwd, apply_verify_code


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', my_login),
    path('accounts/login/', my_login),
    path('logout/', my_logout),
    path('accounts/register/', register),
    path('accounts/reset_passwd/', reset_passwd),
    path('accounts/apply_for_code/', apply_verify_code),
    path('profile/<int:pk>/', profile),
    path('profile/<int:pk>/confirm/', profile_confirm),
    path('profile/<int:pk>/update', profile_update),
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    path('order/', include('apps.order.urls')),
]
