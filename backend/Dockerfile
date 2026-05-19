# Use an official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Hugging Face Spaces run as a non-root user with ID 1000
# We need to create this user and give them permissions
RUN useradd -m -u 1000 user

# Install system dependencies (required for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application
COPY . .

# Create directories required by the application and set ownership to our non-root user
RUN mkdir -p uploads vector_store reports && \
    chown -R user:user /app

# Switch to the non-root user
USER user

# Hugging Face Spaces automatically route traffic to port 7860
EXPOSE 7860

# Command to run the FastAPI application on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
