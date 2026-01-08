FROM rust:1.92 AS builder

WORKDIR /app

# Copy dependency files
COPY Cargo.toml Cargo.lock ./
COPY src ./src

# Build the binary
RUN cargo build --release --bin cloudcheck

FROM debian:trixie-slim

# Install CA certificates for SSL verification
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

# Create non-root user with uid/gid 1000
RUN groupadd -r -g 1000 cloudcheck && useradd -r -u 1000 -g cloudcheck cloudcheck

WORKDIR /app

# Copy the binary from builder
COPY --from=builder /app/target/release/cloudcheck /usr/local/bin/cloudcheck

# Create cache directory with proper permissions
RUN mkdir -p /home/cloudcheck/.cache/cloudcheck && \
    chown -R cloudcheck:cloudcheck /home/cloudcheck/.cache

# Switch to non-root user
USER cloudcheck

ENV RUST_LOG=info

EXPOSE 8080

CMD ["cloudcheck", "serve", "--host", "0.0.0.0", "--port", "8080"]
