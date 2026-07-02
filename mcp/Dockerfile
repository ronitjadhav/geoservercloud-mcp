FROM python:3.12-slim

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy project files (README is required by pyproject's readme field)
COPY pyproject.toml poetry.lock* README.md ./
COPY geoservercloud_mcp ./geoservercloud_mcp/

# Install the package and its dependencies (installs the geoservercloud-mcp entry point)
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# Set environment variables (can be overridden at runtime)
ENV GEOSERVER_URL=http://localhost:8080/geoserver
ENV GEOSERVER_USER=admin
ENV GEOSERVER_PASSWORD=geoserver

# Expose port for HTTP transport
EXPOSE 8000

# Run the MCP server
CMD ["geoservercloud-mcp"]
