FROM python:3.9-slim

WORKDIR /app

COPY . .

# Verify code loads correctly
RUN python3 -c "import sys; print(f'Python {sys.version}')" && \
    python3 -c "from app.server import config; print(f'Config loaded: {config.APP_NAME}')" && \
    python3 -c "from app.minimal_qr import MinimalQR; print('QR module loaded')"

EXPOSE 8080

# Use exec form for proper signal handling
CMD ["python3", "main.py"]
