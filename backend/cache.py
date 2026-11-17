import os
from flask_caching import Cache

cache = Cache()


def init_cache(app):
    """
    Initializes Flask-Caching with Redis as primary backend.
    If Redis server is not reachable on localhost:6379, gracefully falls back
    to in-memory SimpleCache to ensure zero downtime and seamless operation.
    """
    redis_url = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/2")
    cache_type = os.getenv("CACHE_TYPE")

    # If user explicitly specified CACHE_TYPE in environment, respect it
    if cache_type:
        app.config["CACHE_TYPE"] = cache_type
        if cache_type == "RedisCache":
            app.config["CACHE_REDIS_URL"] = redis_url
        cache.init_app(app)
        return cache

    # Auto-detect Redis availability
    try:
        import redis
        r = redis.from_url(redis_url, socket_connect_timeout=0.3, socket_timeout=0.3)
        r.ping()
        app.config["CACHE_TYPE"] = "RedisCache"
        app.config["CACHE_REDIS_URL"] = redis_url
        app.config["CACHE_KEY_PREFIX"] = "trekflow_"
        print("[CACHE] Redis server online: Using RedisCache (db 2)")
    except Exception as e:
        app.config["CACHE_TYPE"] = "SimpleCache"
        print(f"[CACHE] Redis server offline ({e}): Gracefully using SimpleCache")

    app.config.setdefault("CACHE_DEFAULT_TIMEOUT", 300)
    cache.init_app(app)
    return cache
