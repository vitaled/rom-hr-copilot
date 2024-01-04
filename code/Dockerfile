FROM python:3.11.6-slim-bullseye
RUN apt-get update && apt-get install python-tk python3-tk tk-dev -y
COPY ./requirements.txt /usr/local/src/myscripts/requirements.txt
WORKDIR /usr/local/src/myscripts
RUN pip install -r requirements.txt
COPY . /usr/local/src/myscripts
EXPOSE 8080
CMD ["sh","./scripts/start_app.sh"]
