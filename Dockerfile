# Use Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies for ML and OpenCV
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libfontconfig1 \
    libglib2.0-0 \
    libxrender1 \
    libgomp1 \
    wget \
    pkg-config \
    libgfortran5 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for ONNX Runtime
ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV VECLIB_MAXIMUM_THREADS=1
ENV NUMEXPR_NUM_THREADS=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create staticfiles and media directories
RUN mkdir -p staticfiles media

# Expose port
EXPOSE $PORT

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting IntelliFace..."\n\
echo "📊 Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
echo "🗄️ Running migrations..."\n\
python manage.py migrate --noinput || echo "⚠️ Migration failed, continuing..."\n\
echo "🧪 Testing ML features..."\n\
python -c "import onnxruntime; print(f\"ONNX Runtime version: {onnxruntime.__version__}\")" || echo "⚠️ ONNX Runtime test failed"\n\
echo "🌐 Starting Gunicorn..."\n\
exec gunicorn IntelliFace.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120\n' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]