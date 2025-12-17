# Use an official Python runtime as the parent image
FROM python:3.10.12-slim

# Prevent writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies and pipenv
RUN apt-get update \
    && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip pipenv

# Copy only Pipfile and Pipfile.lock and install dependencies inside container
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --ignore-pipfile

# Copy the rest of the application source code
COPY . .

# Expose the port your app runs on
EXPOSE 8050

# Use Gunicorn to serve the Flask/Dash app
CMD ["gunicorn", "wsgi:application", "--bind", "0.0.0.0:8050", "--workers", "4", "--timeout", "120"]