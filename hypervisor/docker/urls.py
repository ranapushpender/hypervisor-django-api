from django.contrib import admin
from django.urls import path,include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from . import views

app_name = "docker"

urlpatterns = [
    path('',views.get_containers),
    #path('<cid>/',views.get_container_stats),
    path('<cid>/terminal/',views.terminal),
    path('<cid>/',views.get_container_stats),
    
]