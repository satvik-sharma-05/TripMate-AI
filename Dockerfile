# Stage 1: build the React app into static files (client/dist).
FROM node:24-slim AS client
WORKDIR /client
COPY client/package*.json ./
RUN npm ci
COPY client/ .
RUN npm run build

# Stage 2: Python server that serves the API and the built React app.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/server
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server/ .
COPY --from=client /client/dist /app/client/dist
EXPOSE 8000
# Render passes the port in $PORT; locally it falls back to 8000.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
