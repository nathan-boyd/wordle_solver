FROM python:3.10

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y google-chrome-stable xvfb xserver-xephyr xclip

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

USER root
COPY requirements.txt /app/requirements.txt
RUN python -m pip install -r /app/requirements.txt

WORKDIR /app
COPY . .

ENV DISPLAY=:1
ENV DEBUG=true
ENV RUNNING_IN_CONTAINER=true

CMD ./scripts/container_start.sh
