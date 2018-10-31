FROM alpine:3.8

RUN mkdir /project
WORKDIR /project
RUN apk update

RUN apk add python3
RUN apk add freetype-dev
RUN apk add build-base
RUN apk add python3-dev

RUN pip3 install --upgrade pip
RUN pip3 install flask
RUN pip3 install pymongo
RUN pip3 install plotly
RUN pip3 install matplotlib

