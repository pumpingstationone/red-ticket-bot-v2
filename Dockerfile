FROM python:3.12-slim

WORKDIR /app

# Install deps first so this layer is cached unless requirements change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py red_ticket_cog.py ./

# Run as a non-root user, and make sure it actually owns what it needs to read
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "bot.py"]
