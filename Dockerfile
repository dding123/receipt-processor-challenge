FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY app.py .

# Expose port 8080
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]