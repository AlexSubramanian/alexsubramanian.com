FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
# Debian base rather than Alpine on purpose: cryptography (via PyJWT[crypto])
# and uvicorn's C extensions all ship manylinux wheels, so there is nothing to
# compile. On Alpine, pip would fall back to building cryptography from source
# and need a Rust toolchain in the image just to install it.
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Unprivileged: this process holds the agent tokens, so it gets no more than it
# needs.
RUN useradd --system --no-create-home --uid 10001 adminapi
USER adminapi

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
