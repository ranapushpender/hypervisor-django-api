# Steps to setup
* Install libvirt and virt-manager
* Install python3 and python3-pip
* Install django-rest-framework django (2 or 3) and django-cors-headers and python-libvirt and pillow
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
