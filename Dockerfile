FROM selenium/standalone-chrome:98.0

USER root

RUN apt-get -y purge python3.8
RUN apt-get -y autoremove

RUN apt-get update && \
	apt-get install -y software-properties-common gcc && \
    	add-apt-repository -y ppa:deadsnakes/ppa

RUN apt-get update && \
	apt-get --reinstall install -y  \
		python3.10-distutils \
                python3.10 

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 99

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

COPY . /app

RUN python3 -m pip install -r /app/requirements.txt

ENV DEBUG=true

CMD python3 /app/main.py
