FROM python:3.11

WORKDIR /app

COPY requirements.txt /app
COPY src /app
COPY .env /app

RUN pip install -r requirements.txt

CMD ["python", "./app.py"]