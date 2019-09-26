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
from . import views

urlpatterns = [
    path('channels/', views.channel_list),
    path('orders/', views.order_list),
    path('order/<int:pk>/', views.order_detail),
    path('order/<int:pk>/update/', views.order_update),
    path('order/<int:pk>/end/', views.end_order),
    path('order/<int:pk>/reject/', views.reject_order),
    path('order/<int:order_pk>/pass_to/', views.pass_order),

    path('order_pool/', views.order_pool_list),
    path('order_pool/<int:pk>/take/', views.order_pool_take),
    path('create/', views.order_create),
    path('import_channel/', views.import_channel),
    path('channel/<int:pk>/', views.channel_detail),
    path('channel/<int:pk>/update/', views.channel_update),
    path('report/', views.report),
]
