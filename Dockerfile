# Use the official Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into the container
COPY . /app/

# Install Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variable to run Django in unbuffered mode
ENV PYTHONUNBUFFERED 1

# Run necessary Django commands (e.g., collectstatic)
RUN python manage.py collectstatic --noinput

# Start the Django server using Gunicorn
CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:8000"]
