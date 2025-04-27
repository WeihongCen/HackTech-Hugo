FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose Flask port (default is 5000)
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
