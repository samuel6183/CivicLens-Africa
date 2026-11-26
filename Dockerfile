FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser && mkdir -p /data && chown appuser /data
COPY backend backend
COPY frontend frontend
USER appuser
ENV CIVICLENS_DB=/data/civiclens.sqlite3
EXPOSE 8000
CMD ["uvicorn","backend.main:app","--host","0.0.0.0","--port","8000"]
