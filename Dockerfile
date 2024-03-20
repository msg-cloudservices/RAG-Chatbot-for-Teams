FROM python:3.11

WORKDIR /app

COPY requirements.txt /app
COPY src /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "app:app"]