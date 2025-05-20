FROM python:3.11-slim

WORKDIR /app

# Install uv for package management
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add uv to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Copy pyproject.toml and install dependencies
COPY pyproject.toml .
RUN uv sync

# Copy application code and support files
COPY graphiti_mcp_server.py .
COPY zep_graphiti.py .
COPY config.py .

# Install required dependencies
RUN pip install surrealdb fastapi uvicorn

# Set up Python path to include the graphiti_core module
ENV PYTHONPATH="/app:${PYTHONPATH}"

EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["uv", "run", "graphiti_mcp_server.py"]
