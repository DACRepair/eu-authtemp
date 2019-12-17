FROM python:3.8-alpine

ENV FLASK_HOST "0.0.0.0"
ENV FLASK_PORT 5000
ENV FLASK_TITLE "Twitch API Portal"
ENV FLASK_SECRET "also top secret"
ENV FLASK_DEBUG "false"
ENV DB_URI "DB URI"
ENV TWITCH_CLIENT "client id"
ENV TWITCH_SECRET "top secret"
ENV TWITCH_REDIRECT ""

WORKDIR /usr/src/app

COPY app.py .
COPY requirements.txt .
COPY App ./App/
COPY static ./static/
COPY templates ./templates/

RUN pip3 install pymysql
RUN pip3 install -r requirements.txt

RUN chmod +x app.py
EXPOSE 5000
CMD ./app.py