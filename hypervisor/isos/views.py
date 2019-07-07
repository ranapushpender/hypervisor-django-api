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

    def create(self, request, *args, **kwargs):
        data = request.data
        data['size']=int(data['file'].size/(1000**2))
        extension = ''
        for i in range(len(data['name'])-1,0,-1):
            if data['name'][i] == '.':
                break
            else:
                extension = data['name'][i] + extension
        data['extension']=extension
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data) 