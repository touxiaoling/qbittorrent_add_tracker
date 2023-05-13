FROM python:3.11-slim

RUN pip install -U setuptools pip

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip3 install  -r /code/requirements.txt
COPY main.py /code/main.py

ENTRYPOINT [ "python3" ,"main.py" ]