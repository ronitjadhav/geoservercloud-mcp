FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY geoservercloud ./geoservercloud/
COPY geoserver_acceptance_tests ./geoserver_acceptance_tests/

# Install dependencies (without dev dependencies, --no-root skips installing the package itself)
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

# Set environment variables (can be overridden at runtime)
ENV GEOSERVER_URL=http://localhost:8080/geoserver
ENV GEOSERVER_USER=admin
ENV GEOSERVER_PASSWORD=geoserver

# Expose port for HTTP transport
EXPOSE 8000

# Run the MCP server
CMD ["poetry", "run", "geoservercloud-mcp"]
