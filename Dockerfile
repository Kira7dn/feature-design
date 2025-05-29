FROM python:3.12-slim

ARG PORT=80

WORKDIR /app

# Install uv and Redis CLI tools for debugging/monitoring
RUN apt-get update && \
    apt-get install -y redis-tools python3-setuptools && \
    pip install uv && \
    rm -rf /var/lib/apt/lists/*

# Copy the MCP server files
COPY . .

# Install packages directly to the system (no virtual environment)
# Combining commands to reduce Docker layers
RUN uv pip install --system -e . && \
    crawl4ai-setup

EXPOSE ${PORT}

# Command to run the FastAPI server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]