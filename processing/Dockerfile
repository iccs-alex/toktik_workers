FROM python:3.9
RUN apt update && apt install -y ffmpeg

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5000
ENV PYTHONUNBUFFERED=true
CMD [ "python", "./app.py" ]
