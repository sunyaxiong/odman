FROM python:3.7.9-alpine3.12
MAINTAINER sunyaxiong <yaxiong.sun@vstecs.com>

EXPOSE 4000
ENV APPNAME=odman

COPY ./* /data/

RUN echo "https://mirror.tuna.tsinghua.edu.cn/alpine/v3.4/main" > /etc/apk/repositories && \
apk add --update \
    gcc && \
mkdir /data/
WORKDIR /data/

CMD ["python" , "manage.py", "runserver", "0.0.0.0:8080"]
