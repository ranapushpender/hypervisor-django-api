import libvirt
import os as OS
import subprocess
import xml.etree.ElementTree as ET
from logging import error as log

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

    def createVM(self,name,cpu,memory,image,size,os,vnc):
        if vnc:
            retcode = subprocess.call(['virt-install','--disk='+name+'.qcow2,size='+str(size),'--name='+name,'--vcpus='+str(cpu),'--memory='+str(memory),'--cdrom=/home/pushpender/Downloads/'+image,'--graphics=vnc,listen=0.0.0.0','--noautoconsole'])
        else:
            retcode = subprocess.call(['virt-install','--disk='+name+'.qcow2,size='+str(size),'--name='+name,'--vcpus='+str(cpu),'--memory='+str(memory),'--cdrom=/home/pushpender/Downloads/'+image])
        log(retcode)
        return(retcode)
    
    def getDomain(self,name):
        return self.con.lookupByName(name)
    
    def getInfo(self,domain):
        info = domain.info()
        return {
                    'name':domain.name(),
                    'state':getState(info[0]),
                    'memory':info[1],
                    'cpus':info[3]
                }

class VMDom:
    dom=None
    def __init__(self,name,connection):
        try:
            self.dom = connection.lookupByName(name)
        except:
            self.dom = None

    def startVM(self):
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
        return {
                    'name':self.dom.name(),
                    'state':getState(info[0]),
                    'memory':info[1],
                    'cpus':info[3]
                }

    def getXML(self):
        print(self.dom.XMLDesc())
    
    def enableCDRom(self,con):
        root=ET.fromstring(self.dom.XMLDesc())
        os = root.find('./os')
        cdrom = ET.Element('boot')
        cdrom.set('dev','cdrom')
        os.append(cdrom)
        log(ET.tostring(os))
        self.dom.undefine()
        self.dom =con.defineXML(ET.tostring(root).decode())
    
    def changeBootDevice(self,con,disk):
        root=ET.fromstring(self.dom.XMLDesc())
        os = root.find('./os')
        disks = os.findall('./boot')

        temp=[]
        for vdisk in disks:
            if vdisk.get('dev') != disk:
                log('VDISK DEV: '+vdisk.get('dev'))
                temp.append(vdisk)
                os.remove(vdisk)

        for ele in temp:
            os.append(ele)

        self.dom.undefine()
        self.dom =con.defineXML(ET.tostring(root).decode())
    
    def mountIso(self,con,name):
        root = ET.fromstring(self.dom.XMLDesc())
        disks = root.findall('./devices/disk')
        for disk in disks:
            if disk.get('device')=='cdrom':
                source = disk.find('./source')
                if source:
                    source.set('file','/home/pushpender/Downloads/'+name+'.iso')
                else:
                    sourceElement = ET.Element('source')
                    sourceElement.set('file','/home/pushpender/Downloads/'+name+'.iso')
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
        disks = root.findall('./devices/disk')
        diskInfo=[]
        for disk in disks:
            diskInfo.append(disk.get('device'))
        return diskInfo
    
    def getMountedIso(self):
        root = ET.fromstring(self.dom.XMLDesc())
        disks = root.findall('./devices/disk')
        for disk in disks:
            if disk.get('device')=='cdrom':
                return disk.find('./source').get('file')
    
    def getState(stateNum):
        if stateNum==1:
            return 'Running'
        elif stateNum==3:
            return 'Paused'
        elif stateNum==5:
            return 'Stopped'

kvm = KVMConnection()
kvm.getConnection()

domain = VMDom('HI-VM-V3',kvm.getConnection())
#domain.unMountIso(kvm.getConnection())
log(domain.getDisks())
#log(domain.getXML())
#domain.mountIso(kvm.getConnection(),'image')
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
        