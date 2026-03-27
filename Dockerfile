FROM python:3.10-slim

WORKDIR /moveinsync

RUN apt-get update && apt-get install -y \
    build-essential \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt /moveinsync/

RUN pip install -upgrade pip && \
    pip install --no-cache-dir -r requiremets.txt
    
COPY . /moveinsync/

EXPOSE 8501

CMD ["streamlit","run","app.py"]

