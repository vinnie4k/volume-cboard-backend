FROM python:3.9

RUN mkdir usr/app
WORKDIR usr/app

COPY . .

RUN pip3 install -r requirements.txt
RUN pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

CMD python src/app.py