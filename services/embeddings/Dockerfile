FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create cache directory for HuggingFace models
RUN mkdir -p /root/.cache/huggingface
ENV HF_HOME=/root/.cache/huggingface

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
