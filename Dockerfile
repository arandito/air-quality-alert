FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SRC_DIR=/app

EXPOSE 8080

CMD ["python", "app.py"]