# Stage 1: Build librdkafka using Debian
FROM debian:bookworm AS builder
ARG LIBRDKAFKA_VERSION=v2.8.0

# Install build dependencies for librdkafka using apt
# Using --no-install-recommends to keep the image smaller
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    git \
    zlib1g-dev \
    libssl-dev \
    libsasl2-dev \
    libzstd-dev \
    bash && \
    rm -rf /var/lib/apt/lists/*

# Clone and build librdkafka
WORKDIR /tmp
RUN git clone https://github.com/confluentinc/librdkafka.git && \
    cd librdkafka && \
    echo "Checking out ${LIBRDKAFKA_VERSION}" && \
    git checkout ${LIBRDKAFKA_VERSION} && \
    ./configure --prefix=/usr && \
    make && \
    make install DESTDIR=/librdkafka-install

# Stage 2: Final Python application image using Debian
FROM python:3.13-bookworm

# Install runtime dependencies for librdkafka and the application using apt
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sqlite3 \
    zlib1g \
    libssl3 \
    libsasl2-2 \
    libzstd1 && \
    rm -rf /var/lib/apt/lists/*

# Copy built librdkafka libraries and headers from the builder stage
COPY --from=builder /librdkafka-install/usr/lib/librdkafka*.so* /usr/lib/
COPY --from=builder /librdkafka-install/usr/include/librdkafka /usr/include/librdkafka

WORKDIR /usr/src/app

# Install Python build dependencies (needed for confluent-kafka build)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libc6-dev && \
    rm -rf /var/lib/apt/lists/*

COPY . /usr/src/app

# Install Python dependencies
# Set flags to help pip find the manually installed librdkafka
ENV LDFLAGS="-L/usr/lib" CPPFLAGS="-I/usr/include"
RUN echo "Installing Python packages..." && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Clean up build dependencies after pip install
RUN apt-get purge -y --auto-remove build-essential python3-dev libc6-dev

EXPOSE 443 9092 8000

RUN chmod +x /usr/src/app/start_demo.sh

# Set the default command to run the application
CMD [ "./start_demo.sh", "example.ini", "default.ini" ]
