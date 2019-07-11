from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from utils.functions import KVMConnection,StoragePool
from logging import error as log
# Create your views here.
@api_view(['GET','POST'])
def pools_view(request):
    conn = KVMConnection()
    if request.method == 'POST':
        data = request.POST
        if data['name'] in StoragePool.listAllPools(conn.getConnection()):
            return Response({'status':'error','message':'Pool already exists'})
        else:
            StoragePool.createPool(conn.getConnection(),data['name'])

    return Response(StoragePool.listAllPoolsInfo(conn.getConnection()))
    #elif request.method=='POST'

@api_view(['GET','POST','DELETE'])
def pool_info_view(request,poolname):
    conn = KVMConnection()
    log(poolname)
    if poolname not in StoragePool.listAllPools(conn.getConnection()):
            return HttpResponse(status=404)
    
    pool = StoragePool(conn.getConnection(),poolname)
    if request.method=='POST':
        data = request.POST
        if data['name'] in pool.getVolumeNames():
            return Response({'status':'error','message':'volume already exists'})
        else:
            pool.createVolume(data['name'],data['size'],data['maxsize'])

    if request.method == 'DELETE':
        pool.deletePool()
        return Response({'status':'ok','message':'Pool deleted successfully'})

    if request.method == 'GET':
        if not pool.isActive() :
            pool.startPool()

    return Response(pool.getPoolInfo())

@api_view(['DELETE'])
def volume_info(request,poolname,volume):
    conn = KVMConnection()
    if request.method == 'DELETE':
        #log(volume)
        pool = StoragePool(conn.getConnection(),poolname)
        pool.deleteVolume(volume)
        return Response(pool.getPoolInfo())