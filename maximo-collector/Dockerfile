FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
RUN addgroup --system app && adduser --system --ingroup app app && chown -R app:app /app
USER app
CMD ["mxcollector", "serve", "--host", "0.0.0.0", "--port", "8002"]
