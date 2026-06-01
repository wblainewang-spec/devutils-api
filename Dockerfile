# Use official Python 3.9 slim image
FROM python:3.9-slim

WORKDIR /app

# Copy the entire application
COPY . .

# Expose the port
EXPOSE 8080

# Debug: verify Python works and files exist
RUN python3 -c "import sys; print(f'Python {sys.version}')" && \
    python3 -c "from app.server import config; print(f'Config loaded: {config.APP_NAME}')" && \
    python3 -c "from app.minimal_qr import MinimalQR; print('QR module loaded')"

# Healthcheck
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:$PORT/health')" || exit 1

# Run the app
CMD python3 main.py
