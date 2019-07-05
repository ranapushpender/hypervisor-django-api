from django.contrib import admin
from django.urls import path,re_path
from . import views
import re

app_name='storages'

urlpatterns = [
    path('',views.pools_view),
    path('<poolname>',views.pool_info_view),
    path('<poolname>/<volume>',views.volume_info)
]