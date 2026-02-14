FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libvirt-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy pyproject.toml first for better caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir uv && \
    uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv pip install fastapi uvicorn pycdlib jinja2 python-dotenv libvirt-python scrypt

# Copy application code
COPY . .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV DATA_DIR=/var/lib/vm-provisioner

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
