# syntax=docker/dockerfile:1.7

# ------------------------------------------------------------------
# Stage 1 — base image
# Use python:3.12-slim: small, official, regularly patched.
# Avoid 'python:latest' (unpredictable) and 'python:3.12' (300MB+).
# A specific tag pins the version so builds are reproducible.
# ------------------------------------------------------------------
FROM python:3.12-slim AS base

# ------------------------------------------------------------------
# Environment variables for Python in containers
#   PYTHONDONTWRITEBYTECODE=1 — don't create .pyc files (smaller image)
#   PYTHONUNBUFFERED=1        — print logs immediately, not buffered
#                               (essential for seeing logs in CI/k8s)
#   PIP_NO_CACHE_DIR=1        — don't keep pip's download cache
# ------------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ------------------------------------------------------------------
# Create a non-root user. NEVER run apps as root in containers.
# If the app is compromised, root inside a container makes it
# much easier to escape into the host.
# We create the user BEFORE copying code so the layer is cached.
# ------------------------------------------------------------------
RUN groupadd --system app && \
    useradd --system --gid app --home /app --shell /usr/sbin/nologin app

# ------------------------------------------------------------------
# Set working directory.
# All subsequent commands run from here.
# ------------------------------------------------------------------
WORKDIR /app

# ------------------------------------------------------------------
# Copy requirements first, install deps, THEN copy code.
# Why this order? Docker caches each layer.
# If you edit app/main.py, only the COPY-code layer is rebuilt;
# the dependency install layer stays cached. Builds become 10x faster.
# ------------------------------------------------------------------
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn==23.0.0

# ------------------------------------------------------------------
# Copy the application code.
# --chown sets ownership in one step (faster than RUN chown).
# ------------------------------------------------------------------
COPY --chown=app:app app/ ./app/
COPY --chown=app:app scripts/ ./scripts/
# ------------------------------------------------------------------
# Switch to the non-root user for everything that follows.
# ------------------------------------------------------------------
USER app

# ------------------------------------------------------------------
# Document which port the app listens on.
# EXPOSE doesn't publish the port — it's documentation for humans
# and tools. Actual publishing happens at 'docker run -p ...'.
# ------------------------------------------------------------------
EXPOSE 5000

# ------------------------------------------------------------------
# Healthcheck — Docker can periodically test if the container
# is alive. Uses Python (already installed) so we don't need to
# add curl just for this.
# ------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; \
        sys.exit(0) if urllib.request.urlopen('http://localhost:5000/health').status==200 else sys.exit(1)"

# ------------------------------------------------------------------
# Start the app with Gunicorn (production WSGI server).
# Flask's built-in server is for development only — single-threaded,
# not robust under load.
# ------------------------------------------------------------------
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app.main:create_app()"]
