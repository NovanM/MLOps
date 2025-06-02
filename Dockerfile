# Gunakan image Python saja (hapus node:alpine yang tidak perlu)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements terlebih dahulu untuk better caching
COPY requirements.txt .

# Install dependencies Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy semua file aplikasi
COPY . .

# Expose port yang sama dengan app.py (3000, bukan 5000)
EXPOSE 3000

# Command untuk menjalankan aplikasi
CMD ["python", "app.py"]
