from django.shortcuts import render,redirect
from django.http import HttpResponse
from utils.functions import KVMConnection,VMDom
from rest_framework.response import Response
from rest_framework.decorators import api_view
from logging import error as log
from isos.models import IsoModel
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Create your views here.
def vmlist_view(request):
    conn= KVMConnection()
    conn.getConnection()
    if(request.method=='POST'):
        domain = VMDom(request.POST['vmname'],conn.getConnection())
        if(request.POST['action']=='stop'):
            domain.shutdownVM()
        elif(request.POST['action']=='forcestop'):
            domain.forceStopVM()
        elif(request.POST['action']=='start'):
            domain.startVM()
        conn.closeConnection()
        return redirect('virtualmachines:vmlist')
    else:
        inactiveVM=conn.listVM()['inactive']
        activeVM= conn.listVM()['active']
        conn.closeConnection()
        return render(request,'virtualmachines/vmlist.html',{'activevm':activeVM,'inactivevm':inactiveVM})


@api_view(['GET','POST'])
def vms_view(request):
    conn= KVMConnection()
    conn.getConnection()
    
    if request.method=='GET':
        vmsInfo=conn.listVM()
        conn.closeConnection()
        return Response(vmsInfo)

    elif request.method=='POST':
        data= request.POST
        iso = IsoModel.objects.get(id=data['image'])
        isoname = iso.file.name
        vnc=False
        if(data['vnc']):
            vnc=True
        
        retcode = conn.createVM(data['name'],data['cpu'],data['memory'],BASE_DIR+'/media/'+isoname,data['pool'],data['volume'],data['os'],vnc)
        conn.closeConnection()
        
        responseObj={}
        if(retcode==0):
            responseObj['status']='ok'
            responseObj['message']='Machine created successfully'
        else:
            responseObj['status']='error'
            responseObj['message']='Machine creation failed'

        return Response(responseObj)


@api_view(['GET','PUT','DELETE','POST'])
def vmdetail_view(request,vmname):
    conn= KVMConnection()
    conn.getConnection()
    responseObj={}
    domain = VMDom(vmname,conn.getConnection())
    if(domain.dom==None):
        return HttpResponse(status=404)

    if request.method=='POST':
        if(request.POST['action']=='stop'):
            domain.shutdownVM()
        elif(request.POST['action']=='forcestop'):
            domain.forceStopVM()
        elif(request.POST['action']=='start'):
            log('Startign VM')
            domain.startVM()
        elif request.POST['action']=='mount':
            if not request.POST['isoid']:
                return HttpResponse(status=404)
            else:
                isopath = BASE_DIR+'/media/' + IsoModel.objects.get(id=request.POST['isoid']).file.name
                domain.mountIso(conn.getConnection(),isopath)
        elif request.POST['action']=='unmount':
            domain.unMountIso(conn.getConnection())
        elif request.POST['action']=='bootdevice':
            domain.changeBootDevice(conn.getConnection(),request.POST['device'])
        elif request.POST['action']=='enablecd':
            domain.enableCDRom(conn.getConnection())
        responseObj= domain.getInfo()
        
    
    elif request.method=='GET':
        responseObj= domain.getInfo()

    conn.closeConnection()
    return Response(responseObj)



def vmcreate_view(request):
    conn=KVMConnection()
    conn.getConnection()
    if(request.method=='POST'):
        data= request.POST
        log(request.POST)
        vnc=False
        if(data['vnc']):
            vnc=True
        conn.createVM(data['name'],data['cpu'],data['memory'],data['image'],data['disk'],data['os'],vnc)
        conn.closeConnection()
        return redirect('virtualmachines:vmlist')
    return render(request,'virtualmachines/vmcreate.html')

def vmmanage_view(request,slug):
    conn=KVMConnection()
    domain = VMDom(slug,conn.getConnection())
    return render(request,'virtualmachines/vmmanage.html',{'slug':slug})