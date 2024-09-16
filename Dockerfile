# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Start Gunicorn to serve the Flask app
CMD ["gunicorn", "-b", "0.0.0.0:8000", "bot:app"]
