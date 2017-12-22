FROM ubuntu:16.04
MAINTAINER Michael P. Jung

RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:fkrull/deadsnakes
RUN apt-get update
RUN apt-get install -y python python2.7 python3.2 python3.3 python3.4 python3.5 python3.6 virtualenv

RUN virtualenv /djc-env
RUN /djc-env/bin/pip install tox

COPY . /djc/

WORKDIR /djc/
CMD /djc-env/bin/tox
