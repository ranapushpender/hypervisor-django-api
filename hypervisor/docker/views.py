from django.shortcuts import render,redirect
from django.http import HttpResponse
from utils.functions import KVMConnection,VMDom,Container,Docker,Terminal
from rest_framework.response import Response
from rest_framework.decorators import api_view
from logging import error as log
from isos.models import IsoModel
import jwt
import os
import datetime
from rest_framework import status
import json

#TODO : MAke docker singleton

@api_view(['GET','POST'])
def get_containers(request):
    docker = Docker()
    errors = None
    if request.method == "POST":
        log("Creating container : "+request.POST["options"])
        errors = docker.createContainer(request.POST["options"])[1]
        log(errors)

    containers = {
        "payload" : [vars(container) for container in docker.getContainers()]
    }
    if len(containers)<=0:
        return Response(containers,status=status.HTTP_204_NO_CONTENT)
    containers["error"] = errors
    return Response(containers,status=status.HTTP_200_OK)

@api_view(['GET','POST','DELETE'])
def get_container_stats(request,cid):
    docker = Docker()
    container = docker.findContainer(cid)
    if container==None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method=="POST":
        action = request.POST["action"]
        if action=="start":
            container.start()
        elif action=="stop":
            container.stop()
    elif request.method=="DELETE":
        container.delete()
        return Response(status = status.HTTP_200_OK)
    response = container.stats()
    st = container.inspect()
    st = st[1:len(st)-1:]
    st = json.loads(st)
    for key,value in vars(container).items():
        response[key] = value
        
    for key,value in st.items():
        response[key] = value
    #log(st)
    return Response(response)

@api_view(['POST'])
def terminal(request,cid):
    docker = Docker()
    if docker.findContainer(cid)==None:
        return Response(cid,status=status.HTTP_404_NOT_FOUND)
    else:
        if request.method=="POST":
            terminal = Terminal()
            terminal.connect(cid)
            return Response(terminal.send_command(request.POST["cmd"]))
            

