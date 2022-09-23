FROM python:3.8-slim-buster

MAINTAINER Brandon Spendlove <brandon.spendlove@veesix-networks.co.uk>

# Leverage Docker layer caching
COPY ./requirements.txt /exabgp/requirements.txt

# Install requirements
RUN pip install --upgrade pip
RUN pip install -r /exabgp/requirements.txt

# Change Workdirectory
WORKDIR /exabgp
COPY . /exabgp

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]