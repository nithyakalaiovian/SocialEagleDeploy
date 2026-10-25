FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY 01Frontend ./01Frontend
COPY 02Backend ./02Backend

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "01Frontend/app.py", "--server.address=0.0.0.0", "--server.port=8501"]