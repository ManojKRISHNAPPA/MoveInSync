FROM python:3.10-slim

# Create non-root user (security best practice)
RUN useradd -m appuser

WORKDIR /moveinsync

# Install build dependencies and clean up in one layer
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /moveinsync/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and set ownership
COPY . /moveinsync/
RUN chown -R appuser:appuser /moveinsync

# Switch to non-root user
USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
