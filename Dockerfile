FROM python:3.12.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd -r default_user && useradd -r -g default_user -m -d /app -s /usr/sbin/nologin default_user

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Nur bei Bedarf anwenden!!! In dem Fall hat der User auch Schreibrechte auf die App.
# RUN chown -R default_user:default_user /app
RUN chown -R root:root /app && \
    chmod -R 755 /app

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/Willkommen', timeout=5).read()"]

USER default_user

CMD ["python", "main.py", "-P", "5000", "-H", "0.0.0.0", "--no-reloader"]
