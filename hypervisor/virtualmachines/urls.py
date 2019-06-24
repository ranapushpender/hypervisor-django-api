from django.contrib import admin
from django.urls import path
from . import views

app_name='virtualmachines'

urlpatterns = [
    path('',views.vmlist_view,name='vmlist')
]