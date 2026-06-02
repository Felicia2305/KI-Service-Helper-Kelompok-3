FROM python:3.10-slim

WORKDIR /app

# Install dependencies dari folder backend
COPY 03_Source_Code/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh isi folder backend ke /app
COPY 03_Source_Code/backend/ .

# Port Hugging Face
ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]