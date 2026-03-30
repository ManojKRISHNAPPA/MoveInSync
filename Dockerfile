FROM python:3.10-slim

WORKDIR /moveinsync

# Install build-essential and clean up
RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt /moveinsync/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . /moveinsync/

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]