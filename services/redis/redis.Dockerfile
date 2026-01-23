FROM redis:7-alpine

# Create directory for Redis data
RUN mkdir -p /data

# Expose Redis port
EXPOSE 6379

# Set volume for cache persistence
VOLUME ["/data"]

# Configure Redis for cache use with maxmemory policy
# Using LRU (Least Recently Used) eviction policy suitable for caching
CMD ["redis-server", \
     "--appendonly", "yes", \
     "--appendfsync", "everysec", \
     "--maxmemory", "256mb", \
     "--maxmemory-policy", "allkeys-lru"]
