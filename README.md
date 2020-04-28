# Steps to setup
* Install libvirt and virt-manager
* Install python3 and python3-pip
* Install django-rest-framework django (2 or 3) and django-cors-headers and python-libvirt and pillow and websockets, asyncio, pyjwt
* create mypools directory in home folder
* Install nodejs 12 lts it will install npm also
* Start default network using virsh
* Run ttyd-command.txt's command
* Install docker
* Go to websockify run its command.txt
* Run npm install
* Run python3 manage.py runserver as root
* Run npm start as non root
* You can proxy docker.sock using nginx and send http requests to it gist has notes. View docker engine api for formats
* For ttyd install : - sudo apt-get install libwebsockets-dev
* Use Socat command sudo socat TCP-LISTEN:8800,reuseaddr,fork UNIX-CONNECT:/var/run/docker.sock to make doker socket of api engine available at a port and ip
* run doker-python-websoket program using python3 TerminalSocket.py as sudo
* You can proxy docker.sock using nginx and send http requests to it gist has notes. View docker engine api for forma
* add your user to docker and libvirt groups to run without sudo
* # Note : If running python as root please run sudo python -m pip install else module will be installed as normal user
* BUG: start stop the default pool from virt manager  else the project will not detect pools
* require cors for websockify, terminal etc
* BUG: volume list loaded by default is for wrong pool
* Incase of using manjaro install libvirt acording to arch guide and enable docker service , libvirtd , and go to /etc/libvirt/qemu.conf find users =  and groups = and add your username of the current user instead of root
