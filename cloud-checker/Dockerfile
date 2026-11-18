FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY check.py schedule.json ./
USER 65534:65534
CMD ["python", "-u", "check.py"]
