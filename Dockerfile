FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    poppler-utils

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Flask port (default is 5000)
EXPOSE 8080

# Run the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
