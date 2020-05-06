FROM alpine
RUN mkdir /src
RUN mkdir /src/app
WORKDIR /tmp
RUN apk add --no-cache python3
COPY . /tmp
RUN python3 setup.py install
RUN python3 -m pip install pyjwt
WORKDIR /src/app
EXPOSE 6080/tcp
CMD /bin/sh /src/app/run 6080 --token-plugin JWTTokenApi