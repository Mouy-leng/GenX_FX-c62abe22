/**
 * Response Caching Middleware
 * Implements in-memory caching for API responses to reduce database load
 */

class ResponseCache {
  constructor(ttl = 60) {
    this.cache = new Map();
    this.ttl = ttl * 1000; // Convert to milliseconds
  }

  /**
   * Generate cache key from request
   */
  generateKey(req) {
    const { method, originalUrl, user } = req;
    const userId = user ? user.id : 'anonymous';
    return `${method}:${originalUrl}:${userId}`;
  }

  /**
   * Get cached response
   */
  get(key) {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp > this.ttl) {
      // Cache expired, remove it
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  /**
   * Set cached response
   */
  set(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  /**
   * Clear cache entry or entire cache
   */
  clear(key = null) {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.size,
      ttl: this.ttl / 1000
    };
  }

  /**
   * Clean expired entries (run periodically)
   */
  cleanExpired() {
    const now = Date.now();
    let cleaned = 0;
    
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > this.ttl) {
        this.cache.delete(key);
        cleaned++;
      }
    }
    
    return cleaned;
  }
}

// Create cache instances with different TTLs for different types of data
const caches = {
  short: new ResponseCache(30),    // 30 seconds for frequently changing data
  medium: new ResponseCache(300),   // 5 minutes for semi-static data
  long: new ResponseCache(3600)     // 1 hour for rarely changing data
};

// Periodically clean expired cache entries
setInterval(() => {
  Object.values(caches).forEach(cache => cache.cleanExpired());
}, 60000); // Clean every minute

/**
 * Cache middleware factory
 * @param {string} cacheType - Type of cache to use (short, medium, long)
 */
const cacheMiddleware = (cacheType = 'medium') => {
  const cache = caches[cacheType];
  
  if (!cache) {
    throw new Error(`Invalid cache type: ${cacheType}. Use 'short', 'medium', or 'long'.`);
  }

  return (req, res, next) => {
    // Only cache GET requests
    if (req.method !== 'GET') {
      return next();
    }

    const key = cache.generateKey(req);
    const cached = cache.get(key);

    if (cached) {
      // Return cached response
      return res.status(200).json({
        ...cached,
        _cached: true,
        _cachedAt: new Date().toISOString()
      });
    }

    // Store original json method
    const originalJson = res.json.bind(res);

    // Override json method to cache the response
    res.json = function(data) {
      // Only cache successful responses (status 200-299)
      if (res.statusCode >= 200 && res.statusCode < 300) {
        cache.set(key, data);
      }
      return originalJson(data);
    };

    next();
  };
};

/**
 * Invalidate cache middleware
 * Use this for POST, PUT, DELETE routes that modify data
 */
const invalidateCache = (cacheTypes = ['short', 'medium', 'long']) => {
  return (req, res, next) => {
    cacheTypes.forEach(type => {
      if (caches[type]) {
        // Clear all cache entries for this cache type
        caches[type].clear();
      }
    });
    next();
  };
};

/**
 * Get cache statistics
 */
const getCacheStats = () => {
  return Object.entries(caches).reduce((stats, [type, cache]) => {
    stats[type] = cache.getStats();
    return stats;
  }, {});
};

module.exports = {
  cacheMiddleware,
  invalidateCache,
  getCacheStats,
  caches
};
