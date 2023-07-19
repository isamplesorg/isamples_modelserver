# syntax=docker/dockerfile:1
# Build the main Python app
FROM python:3.9.15

WORKDIR /app

# The installation of the python requirements should be basically the first thing here.  Docker files will re-run steps
# that appear after a step that has changed.  Setting up the python environment is the most time-consuming step; put
# it first so it only executes when it absolutely has to.
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY isamples_metadata .
COPY ./main.py .
COPY ./enums.py .

COPY ./sampledFeature.bin .
COPY ./metadata_models .
COPY ./isamples_modelserver.env .
COPY ./isamples_modelserver_container_startup.sh .

# Start this up in a shell script, per https://goinbigdata.com/docker-run-vs-cmd-vs-entrypoint/
CMD [ "/app/isamples_modelserver_container_startup.sh" ]