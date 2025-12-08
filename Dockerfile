FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

# Системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Копируем requirements для использования кэша
COPY requirements.txt /app/requirements.txt

# Устанавливаем Python-зависимости
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Сбор статических файлов
RUN python manage.py collectstatic --noinput || true

# Копируем код проекта
COPY . /app

EXPOSE 8000

# Проверяем работоспособности веб-сервиса
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=5 \
  CMD curl --fail --silent --show-error http://127.0.0.1:8000/swagger/ || exit 1

# Запускаем встроенный Django сервер
# CMD ["bash", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
CMD ["sh", "-c", "python manage.py gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
