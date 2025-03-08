FROM python:3.11-alpine

RUN apk add --no-cache tesseract-ocr

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ADD config/requirements/ .
RUN pip install --no-cache-dir -r base.txt && \
    pip install --no-cache-dir -r development.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
