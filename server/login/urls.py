"""monitor_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
# from . import views as view
from . import views
urlpatterns = [
    # path('', view.index),
    # path('',admin.site.urls),
    path('regist/',views.regist),
    path('login/', views.login),
    path('home/', views.home),
    path('data_platform/',views.data_platform),
    path('upload/',views.upload),
    path('analysis/',views.analysis),
    path('video_platform/',views.open_video),
]
