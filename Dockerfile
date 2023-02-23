FROM python:3.8-slim-bullseye

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
        curl \
        git \
        libbz2-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        llvm \
        make \
        tk-dev \
        wget \
        xz-utils \
        zlib1g-dev \
        gcc \
        locales \
        python3-venv \
        python3-dev \
        procps
        
RUN echo 'vm.overcommit_memory=1' >> /etc/sysctl.conf

RUN sed -i '/it_IT.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG it_IT.UTF-8  
ENV LANGUAGE it_IT:it  
ENV LC_ALL it_IT.UTF-8

ENV PATH="/home/uwsgi/.local/bin:${PATH}"

COPY requirements.txt .


RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip3 install wheel
RUN pip3 install -r requirements.txt


WORKDIR /app

COPY templates templates
COPY static static
COPY utils.py .
COPY database.py .
COPY main.py .
COPY config.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
