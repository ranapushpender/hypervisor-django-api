FROM alpine
RUN apk add --no-cache libwebsockets-dev
RUN apk add --no-cache bash
EXPOSE 8580/tcp
RUN mkdir /src
RUN mkdir /src/app
CMD ["/src/app/ttyd","-p 8580" ,"bash"]
