"""DeliveryDetectorServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('get_user/<str:name>/', views.get_user),
    path('send_alert/<str:name>/', views.send_alert),
    path('get_all_users/<int:box_num>/', views.get_all_users),
    path('admin/', admin.site.urls),
    path('wifi_QR/', views.wifi_QR,name ='wifi_QR'),
    path('seller_QR/', views.seller_QR, name='seller_QR'),
    path('tamper_alert/<str:name>/<str:alert_msg>/', views.tamper_alert, name='tamper_alert'),
]
