FROM ubuntu:18.04

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone 

RUN apt update && apt install -y \
  openjdk-8-jdk \
  python3-pip \
  python3-tk \
  wget \
  vim \
  git


RUN pip3 install --upgrade pip

RUN pip3 install \
  numpy \
  jupyter \
  requests \
  sklearn_crfsuite \
  spacy\
  requests \
  pandas \
  sklearn \
  rasa \
  tensorflow \
  keras \
  flask \
  pymessenger \
  slackeventsapi \
  webexteamssdk \
  nltk \
  gensim \
  matplotlib \
  pickle-mixin \
  jellyfish \
  textblob \
  nest_asyncio \
  skype-chatbot


EXPOSE 8888
EXPOSE 9000
EXPOSE 5000

RUN python3 -m spacy download en
RUN useradd -ms /bin/bash kuba
RUN adduser kuba sudo

USER kuba
WORKDIR /home/kuba/
RUN python3 -m nltk.downloader all
RUN mkdir /home/kuba/workshop/
WORKDIR /home/kuba/workshop/
RUN git clone https://github.com/codete/oreilly-intelligent-bots
CMD jupyter-notebook --ip=0.0.0.0 --NotebookApp.token='' --NotebookApp.password='' --no-browser --notebook-dir=/home/kuba/workshop/
