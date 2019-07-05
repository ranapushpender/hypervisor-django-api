from django.contrib import admin
from django.urls import path,re_path,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('',views.IsoView)

app_name='isos'

urlpatterns = [
    path('',include(router.urls)),
]