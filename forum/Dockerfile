
FROM python:3.9-slim


RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    bash

# Робочий каталог
WORKDIR /app

COPY . /app/

# Python-залежності
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Налаштування середовища
COPY .env /app/.env

# Команда запуску контейнера
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "forum.wsgi:application"]
