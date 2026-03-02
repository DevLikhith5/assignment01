FROM python:3.11-slim

WORKDIR /app

# Ensure output is unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
