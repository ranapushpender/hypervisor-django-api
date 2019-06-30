from django.shortcuts import render,redirect
from django.http import HttpResponse
from utils.functions import KVMConnection,VMDom
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

def vmcreate_view(request):
    conn=KVMConnection()
    conn.getConnection()
    if(request.method=='POST'):
        data= request.POST
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