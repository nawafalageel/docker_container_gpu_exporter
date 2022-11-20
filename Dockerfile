FROM python:latest

LABEL maintainer Nawaf Alageel 

COPY . .

RUN apt update

RUN apt install -y python3-pip

RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python3", "docker_gpu_exporter_v3.py"]
