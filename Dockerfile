# https://fastapi.tiangolo.com/deployment/docker/#dockerfile
# 
# Probably won't need to add Poetry to the image, but there is a guide
# for it here: 
# https://fastapi.tiangolo.com/deployment/docker/#docker-image-with-poetry

FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# Keep docker image small as possible by not caching
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./isabot /app/isabot
COPY ./env.py /app/env.py
COPY ./main.py /app/main.py

CMD uvicorn main:app --host 0.0.0.0 --port 8000