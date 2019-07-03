storagePoolXML="""
<pool type='dir'>
    <name>mypool</name>
    <target>
        <path>/home/dashley/images</path>
    </target>
</pool>
"""

volumeXML = """
<volume>
    <name>sparse.img</name>
    <allocation unit="G">0</allocation>
    <capacity unit="G">2</capacity>
    <target>
        <format type='qcow2'/>
        <path></path>
    </target>
</volume>
"""