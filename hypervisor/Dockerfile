FROM ubuntu
RUN mkdir /src
RUN mkdir /src/app
WORKDIR /src/app/
RUN apt update
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN export DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime
RUN apt-get install -y tzdata
RUN dpkg-reconfigure --frontend noninteractive tzdata
RUN apt install libvirt-dev -y
RUN pip3 install django-rest-framework
RUN pip3 install django
RUN pip3 install django-cors-headers
RUN pip3 install libvirt-python
RUN pip3 install pillow
RUN pip3 install websockets
RUN pip3 install asyncio
RUN pip3 install pyjwt
RUN apt install virt-manager -y
RUN apt install docker.io
EXPOSE 8000/tcp
CMD python3 manage.py runserver 0.0.0.0:8000
