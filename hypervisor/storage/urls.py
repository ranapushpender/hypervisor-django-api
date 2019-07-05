from django.contrib import admin
from django.urls import path,re_path
from . import views
import re

app_name='virtualmachines'

urlpatterns = [
    path('',views)
]