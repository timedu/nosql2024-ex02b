FROM python:3.12-slim
WORKDIR /home/app
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# RUN pip install neo4j
# RUN pip install prettytable
# RUN pip install PyYAML
