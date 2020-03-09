FROM python:3.8.1-buster

RUN apt update && apt upgrade -y && \
    apt install cmake -y

RUN git -c http.sslVerify=false clone --recursive http://github.com/Kisensum/pydnp3 && \
    cd pydnp3 && \
    python setup.py install

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY *.py /home/appuser/