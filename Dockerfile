FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Instala direto, sem precisar de pacotes extras do Linux
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]