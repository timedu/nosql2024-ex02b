FROM python:3.12-slim
RUN pip install --upgrade pip
RUN pip install neo4j
RUN pip install prettytable
RUN pip install PyYAML
WORKDIR /home/app
