# Use Ubuntu as the base image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system packages and Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv build-essential curl && \
    apt-get clean

# Copy all app code
COPY . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

