from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import IsoModel
from logging import error as log
from rest_framework import viewsets
from .serializers import IsoSerializer
# Create your views here.
class IsoView(viewsets.ModelViewSet):
    queryset =  IsoModel.objects.all()
    serializer_class = IsoSerializer