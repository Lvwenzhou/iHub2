"""iHub2 URL Configuration

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
from django.urls import path
import iHubSite.views as site_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', site_view.login),
    path('logout/', site_view.logout),
    path('register/', site_view.register),
    path('index/', site_view.index),
    path('my/', site_view.my),
    path('carpool_index/', site_view.carpool_index),
    path('carpool_join/', site_view.carpool_join),
    path('carpool_my/', site_view.carpool_my),
    path('carpool_start/', site_view.carpool_start),
    path('carpool_quit/', site_view.carpool_quit),
    path('carpool_cancel/', site_view.carpool_cancel),
    path('carpool_take_part/', site_view.carpool_take_part),
    path('carpool_map/', site_view.carpool_map),
    path('carpool_search/', site_view.carpool_search),
    path('study_index/', site_view.study_index),
    path('study_join/', site_view.study_join),
    path('study_my/', site_view.study_my),
    path('study_start/', site_view.study_start),
    path('study_quit/', site_view.study_quit),
    path('study_cancel/', site_view.study_cancel),
    path('study_take_part/', site_view.study_take_part),
    path('study_search/', site_view.study_search),
]
