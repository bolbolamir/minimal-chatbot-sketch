FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1

WORKDIR /app
COPY main.py ./
COPY insurance_assistant/ ./insurance_assistant/

USER 10001:10001
ENTRYPOINT ["python", "main.py"]
