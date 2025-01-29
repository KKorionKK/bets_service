FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY common /app/common
COPY run_bet_maker.py /app/run_bet_maker.py
COPY run_line_provider.py /app/run_line_provider.py
COPY .env /app/.env

ENV PYTHONPATH=/app

CMD ["python"]