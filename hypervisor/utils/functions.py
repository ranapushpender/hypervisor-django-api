import libvirt
import os as OS
import subprocess
import xml.etree.ElementTree as ET
from logging import error as log
from uuid import uuid4
from .xmls import storagePoolXML,volumeXML

poolpath='/home/pushpender/mypools/'

class KVMConnection:
    
    LIBVIRT_URL = 'qemu:///system'
    con = None
    def getConnection(self):
        if self.con==None:
            self.con = libvirt.open(self.LIBVIRT_URL)
            if self.con==None:
                print('Error Connecting')
                exit(1)
        return self.con

    def closeConnection(self):
        if self.con != None:
            self.con.close()
            self.con=None
    
    def listVM(self):
        if self.con!= None:
            activeIds = self.con.listDomainsID()
            activeInfo=[]
            for aid in activeIds:
                activeDomain = self.con.lookupByID(aid)
                info = self.getInfo(activeDomain)
                activeInfo.append(info)
            
            inactiveNames = self.con.listDefinedDomains()
            inactiveInfo=[]
            for iname in inactiveNames:
                inactiveDomain  = self.con.lookupByName(iname)
                info = self.getInfo(inactiveDomain)
                inactiveInfo.append(info)
            return {'active':activeInfo,'inactive':inactiveInfo}

    def createVM(self,name,cpu,memory,imagepath,poolname,volname,os,vnc):
        pool = StoragePool(self.con,poolname)
        if pool==None:
            return 1
        volume = pool.getVolume(volname)
        if volume == None:
            return 1
        volpath = ET.fromstring(volume.XMLDesc()).find('./target/path').text
        if vnc:
            retcode = subprocess.call(['virt-install','--disk='+volpath+',device=disk,bus=virtio','--name='+name,'--vcpus='+str(cpu),'--memory='+str(memory),'--cdrom='+imagepath,'--graphics=vnc,listen=0.0.0.0','--noautoconsole'])
        else:
            retcode = subprocess.call(['virt-install','--disk='+volpath+',device=disk,bus=virtio ','--name='+name,'--vcpus='+str(cpu),'--memory='+str(memory),'--cdrom='+imagepath])
        log(retcode)
        return(retcode)
    
    def getDomain(self,name):
        return self.con.lookupByName(name)
    
    def getInfo(self,domain):
        info = domain.info()
        infoObj = {
                    'name':domain.name(),
                    'state':getState(info[0]),
                    'memory':info[1],
                    'cpus':info[3],
                    'os':'Ubuntu',
                }
        if(info[0]==1):
            infoObj['action']='stop'
        else:
            infoObj['action']='start'
        return infoObj

class VMDom:
    dom=None
    def __init__(self,name,connection):
        try:
            self.dom = connection.lookupByName(name)
        except:
            self.dom = None

    def startVM(self):
        log('started')
        self.dom.create()

    def shutdownVM(self):
        self.dom.shutdown()

    def forceStopVM(self):
        self.dom.destroy()

    def getVNCPort(self):
        root=ET.fromstring(self.dom.XMLDesc())
        vnc=root.find('./devices/graphics')
        port=vnc.get('port')
        return port

    def setVNCPassword(self,pwd,con):
        root=ET.fromstring(self.dom.XMLDesc())
        root.find('./devices/graphics').set('passwd',pwd)
        result=ET.tostring(root).decode()
        if self.dom.isActive():
            self.dom.destroy()
        self.dom.undefine()
        xmlC=con.defineXML(result)
        if(xmlC==None):
            print('WTF')
        else:
            xmlC.create()
        return xmlC
   
    def getInfo(self):
        info = self.dom.info()
        obj = {
                    'name':self.dom.name(),
                    'state':getState(info[0]),
                    'memory':info[1],
                    'cpus':info[3],
                    'iso:':self.getMountedIso(),
                    'disks':self.getDisks(),
                    'os':'Ubuntu'
                }
        if info[0]==1:
            obj['action']='stop'
            obj['cpu-usage']=self.getCpuStats()
            obj['memory-usage']=self.getMemoryStats()
        else:
            obj['action']='start'
        return obj

    def getXML(self):
        print(self.dom.XMLDesc())
    
    def enableCDRom(self,con):
        root=ET.fromstring(self.dom.XMLDesc())
        os = root.find('./os')
        cdrom = ET.Element('boot')
        cdrom.set('dev','cdrom')
        os.append(cdrom)
        #log(ET.tostring(os))
        self.dom.undefine()
        self.dom =con.defineXML(ET.tostring(root).decode())
    
    def changeBootDevice(self,con,disk):
        root=ET.fromstring(self.dom.XMLDesc())
        os = root.find('./os')
        disks = os.findall('./boot')

        temp=[]
        for vdisk in disks:
            if vdisk.get('dev') != disk:
                #log('VDISK DEV: '+vdisk.get('dev'))
                temp.append(vdisk)
                os.remove(vdisk)

        for ele in temp:
            os.append(ele)
        #log(ET.tostring(root).decode())
        self.dom.undefine()
        self.dom =con.defineXML(ET.tostring(root).decode())
    
    def mountIso(self,con,isopath):
        root = ET.fromstring(self.dom.XMLDesc())
        disks = root.findall('./devices/disk')
        log('Mount iso path: '+isopath)
        for disk in disks:
            if disk.get('device')=='cdrom':
                source = disk.find('./source')
                if source:
                    source.set('file',isopath)
                else:
                    sourceElement = ET.Element('source')
                    sourceElement.set('file',isopath)
                    disk.append(sourceElement)
        #log(ET.tostring(root).decode())
        self.dom.undefine()
        self.dom = con.defineXML(ET.tostring(root).decode())
    
    def unMountIso(self,con):
        root = ET.fromstring(self.dom.XMLDesc())
        disks = root.findall('./devices/disk')
        for disk in disks:
            if disk.get('device')=='cdrom':
                log('Found disk')
                source = disk.find('./source')
                log(source)
                if source!=None:
                    log('removing source')
                    disk.remove(source)
        #log(ET.tostring(root).decode())
        self.dom.undefine()
        self.dom = con.defineXML(ET.tostring(root).decode())

    def getDisks(self):
        root = ET.fromstring(self.dom.XMLDesc())
        disks = root.findall('./os/boot')
        diskInfo=[]
        for disk in disks:
            diskInfo.append(disk.get('dev'))
        return diskInfo
    
    def getMountedIso(self):
        root = ET.fromstring(self.dom.XMLDesc())
        disks = root.findall('./devices/disk')
        for disk in disks:
            if disk.get('device')=='cdrom':
                if disk.find('./source') != None:
                    isopath= disk.find('./source').get('file')
                else:
                    return None
                isoname=""
                for i in range(len(isopath)-1,0,-1):
                    if(isopath[i]=='/'):
                        break
                    else:
                        isoname = isopath[i] + isoname
                return isoname
    
    def getBootDevices(self):
        root = ET.fromstring(self.dom.XMLDesc())
        bootDevices = []
        disks = root.find('./os').findall('./boot')
        for disk in disks:
            bootDevices.append(disk.get('dev'))
        return bootDevices
    
    def setRam(self,ram):
        self.dom.setMemory(ram)
        return 1
    
    def setCpu(self,cpus):
        self.dom.setVcpus(cpus)

    def getCpuStats(self):
        log(self.dom.getCPUStats(True))
        return self.dom.getCPUStats(True)[0].get('cpu_time')/1000000000

    def getMemoryStats(self):
        return self.dom.memoryStats().get('actual')
    
class StoragePool:
    pool=None
    def __init__(self,con,poolname='default'):
        self.pool = con.storagePoolLookupByName(poolname)
    
    def isAvailable(self):
        if self.pool == None:
            return False
        else:
            return True
    
    def getXML(self):
        return self.pool.XMLDesc()

    def isActive(self):
        return self.pool.isActive()
    
    def startPool(self):
        if self.pool!=None:
            self.pool.create()

    def deletePool(self):
        if self.pool!=None:
            self.pool.undefine()

    def stopPool(self):
        if self.pool!=None:
            self.pool.stop()

    def isAutoStart(self):
        return self.pool.autostart()

    def toggleAutoStart(self):
        self.pool.setAutostart(not self.pool.autostart())

    def getPoolInfo(self):
        info = self.pool.info()
        return{
            'name':self.pool.name(),
            'uuid':self.pool.UUIDString(),
            'volumes':self.pool.numOfVolumes(),
            'state':info[0],
            'capacity':info[1],
            'allocation':info[2],
            'available':info[3],
            'volumes':self.getVolumeInfo()
        }

    def getVolume(self,name):
        return self.pool.storageVolLookupByName(name)

    def getVolumeNames(self):
        return self.pool.listVolumes()
    
    def getVolumeInfo(self):
        volumes = []
        volNames = self.pool.listVolumes()
        for name in volNames:
            volInfo=self.pool.storageVolLookupByName(name).info()
           # log(self.pool.storageVolLookupByName(name).XMLDesc())
            vol ={
                'name':name,
                'type':volInfo[0],
                'capacity':volInfo[1],
                'allocation':volInfo[2]
            }
            volumes.append(vol)
        return volumes
            
    def createVolume(self,name,allocation,max_size):
        #log(name,allocation,max_size)
        #return 0
        if name+'.qcow2' in self.pool.listVolumes():
            return -1
        xmlData= volumeXML
        root = ET.fromstring(xmlData)
        root.find('./name').text=name+'.qcow2'
        root.find('./allocation').text=str(allocation)
        root.find('./capacity').text=str(max_size)
        root.find('./target').find('./path').text=poolpath+str(self.getPoolInfo().get('name'))+'/'+name+'.qcow2'
        ret = self.pool.createXML(ET.tostring(root).decode())
        return ret

    def deleteVolume(self,name):
        log('starting delete of '+name)
        if name in self.pool.listVolumes():
            volume = self.pool.storageVolLookupByName(name)
            #volume.wipe(0)
            volume.delete(0)

    @staticmethod
    def listAllPools(con):
        pools = con.listAllStoragePools(0)
        poolNames = []
        for pool in pools:
            poolNames.append(pool.name())
        return poolNames
    
    @staticmethod
    def createPool(con,name):
        if name in StoragePool.listAllPools(con):
            return -1
        else:
            retcode = subprocess.call(['mkdir',poolpath+name])
            if retcode!=0:
                #return -1
                print('Exists')

            xmlData = storagePoolXML
            root = ET.fromstring(xmlData)
            root.find('./name').text=name
            root.find('./target').find('./path').text='/home/pushpender/mypools/'+name
            con.storagePoolDefineXML(ET.tostring(root).decode())
            return 1


def getState(stateNum):
    if stateNum==1:
        return 'Running'
    elif stateNum==3:
        return 'Paused'
    elif stateNum==5:
        return 'Stopped'

kvm = KVMConnection()
kvm.getConnection()
log(StoragePool.listAllPools(kvm.getConnection()))
#log(StoragePool.listAllPools(kvm.getConnection()))
#defaultPool = StoragePool.listAllPools(poolname='pisty',kvm.getConnection())[0]
#log(StoragePool.createPool(kvm.getConnection(),'pisty'))
#pool = StoragePool(kvm.getConnection(),poolname='pisty')
#pool.deletePool()
#pool.getVolumeInfo()
#log(pool.getVolumeInfo())
#pool.stopPool()
#domain = VMDom('generic',kvm.getConnection())
#log(domain.getXML())
#pool = StoragePool(kvm.getConnection())
#print(pool.isAvailable())
#pool.getInfo()
#log(domain.getMemoryStats())
#log(domain.getBootDevices())
#domain.unMountIso(kvm.getConnection())
#log(domain.getDisks())
#log(domain.getXML())
#domain.mountIso(kvm.getConnection(),'image')
#log(domain.getMountedIso())
#omain.changeBootDevice(kvm.getConnection(),'cdrom')
#domain.changeBootDevice(kvm.getConnection(),'hd')
#domain.getDiskInfo(kvm.getConnection())
#kvm.closeConnection()
#name = connect.listVM()
#print(name)

#print(domain.getVNCPort())
#domain.setVNCPassword('12345',connect.getConnection())
#print(domain.getVNCPort())
#kvm.createVM('HI-VM-V3',1,256,'image.iso',1,'Ubuntu',1)
        