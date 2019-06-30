from django.contrib import admin
from django.urls import path,re_path
from . import views
import re

app_name='virtualmachines'

urlpatterns = [
    path('create/',views.vmcreate_view,name='vmcreate'),
    re_path(r'^manage/(?P<slug>[\w-]+)/$',views.vmmanage_view,name='vmmanage'),
    path('',views.vmlist_view,name='vmlist')
]