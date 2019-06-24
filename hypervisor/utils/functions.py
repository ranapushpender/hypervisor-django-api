import libvirt
import os as call
import xml.etree.ElementTree as ET

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
            active = self.con.listDomainsID()
            activeNames=[]
            for vm in active:
                activeNames.append(self.con.lookupByID(vm).name())
            inactive = self.con.listDefinedDomains()
            return {'active':activeNames,'inactive':inactive}

    def createVM(self,name,cpu,memory,image,size,os,vnc):
        cmd='virt-install --name='+name+' --vcpus='+str(cpu)+' --memory='+str(memory)+' --cdrom=/home/pushpender/Downloads/'+image+' --disk path=/home/pushpender/'+name+'.disk'+',size='+str(size);
        if(vnc):
            cmd=cmd + ' --os-variant=debian8 --graphics vnc,listen=0.0.0.0 --noautoconsole'
        call.system(cmd)
    
    def getDomain(self,name):
        return self.con.lookupByName(name)

class VMDom:
    dom=None
    def __init__(self,name,connection):
        self.dom = connection.lookupByName(name)

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

    def getXML(self):
        print(self.dom.XMLDesc())


#connect = KVMConnection()
#connect.getConnection()
#name = connect.listVM()['active'][0]
#domain = VMDom(name,connect.getConnection())
#print(domain.getVNCPort())
#domain.setVNCPassword('12345',connect.getConnection())
#print(domain.getVNCPort())
#connect.createVM('HI-VM-V3',1,1024,'image.iso',4,'Ubuntu',1)
        