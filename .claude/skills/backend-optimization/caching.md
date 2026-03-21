# Caching Patterns - api

## In-Memory LRU Cache

### 1. Basic LRU Cache

```typescript
import LRU from 'lru-cache';

// Create cache with options
const cache = new LRU<string, any>({
  max: 500, // Maximum items
  maxAge: 1000 * 60 * 5, // 5 minutes TTL
  updateAgeOnGet: true, // Refresh TTL on access
});

// Usage
async function getUser(userId: string) {
  const cacheKey = `user:${userId}`;

  // Check cache
  const cached = cache.get(cacheKey);
  if (cached) return cached;

  // Fetch from DB
  const user = await User.findById(userId);

  // Store in cache
  if (user) {
    cache.set(cacheKey, user);
  }

  return user;
}
```

### 2. Cache Service

```typescript
// services/cache.service.ts
import LRU from 'lru-cache';

class CacheService {
  private cache: LRU<string, any>;

  constructor() {
    this.cache = new LRU({
      max: 1000,
      maxAge: 1000 * 60 * 10, // 10 minutes
    });
  }

  async getOrSet<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    const cached = this.cache.get(key);
    if (cached !== undefined) {
      return cached as T;
    }

    const value = await fetcher();
    this.cache.set(key, value, ttl);
    return value;
  }

  invalidate(key: string): void {
    this.cache.del(key);
  }

  invalidatePattern(pattern: string): void {
    const regex = new RegExp(pattern);
    this.cache.forEach((_, key) => {
      if (regex.test(key)) {
        this.cache.del(key);
      }
    });
  }

  clear(): void {
    this.cache.reset();
  }
}

export const cacheService = new CacheService();
```

### 3. Usage in Service Layer

```typescript
// services/product.service.ts
class ProductService {
  async getProduct(productId: string) {
    return cacheService.getOrSet(
      `product:${productId}`,
      () => Product.findById(productId).lean()
    );
  }

  async getProductsByCategory(category: string) {
    return cacheService.getOrSet(
      `products:category:${category}`,
      () => Product.find({ category }).lean(),
      1000 * 60 * 2 // 2 minutes
    );
  }

  async updateProduct(productId: string, data: UpdateProductDTO) {
    const product = await Product.findByIdAndUpdate(productId, data, { new: true });

    // Invalidate related caches
    cacheService.invalidate(`product:${productId}`);
    cacheService.invalidatePattern(`products:category:.*`);

    return product;
  }
}
```

## Redis Caching

### 1. Redis Connection

```typescript
// config/redis.ts
import Redis from 'ioredis';

const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  password: process.env.REDIS_PASSWORD,
  maxRetriesPerRequest: 3,
  retryDelayOnFailover: 100,
});

redis.on('error', (err) => {
  console.error('Redis error:', err);
});

export default redis;
```

### 2. Redis Cache Service

```typescript
// services/redis-cache.service.ts
import redis from '../config/redis';

class RedisCacheService {
  async get<T>(key: string): Promise<T | null> {
    const data = await redis.get(key);
    return data ? JSON.parse(data) : null;
  }

  async set(key: string, value: any, ttlSeconds: number = 300): Promise<void> {
    await redis.setex(key, ttlSeconds, JSON.stringify(value));
  }

  async getOrSet<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttlSeconds: number = 300
  ): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached !== null) {
      return cached;
    }

    const value = await fetcher();
    await this.set(key, value, ttlSeconds);
    return value;
  }

  async invalidate(key: string): Promise<void> {
    await redis.del(key);
  }

  async invalidatePattern(pattern: string): Promise<void> {
    const keys = await redis.keys(pattern);
    if (keys.length > 0) {
      await redis.del(...keys);
    }
  }

  // Hash operations for structured data
  async hget<T>(key: string, field: string): Promise<T | null> {
    const data = await redis.hget(key, field);
    return data ? JSON.parse(data) : null;
  }

  async hset(key: string, field: string, value: any): Promise<void> {
    await redis.hset(key, field, JSON.stringify(value));
  }

  async hgetall<T>(key: string): Promise<Record<string, T>> {
    const data = await redis.hgetall(key);
    const result: Record<string, T> = {};
    for (const [field, value] of Object.entries(data)) {
      result[field] = JSON.parse(value);
    }
    return result;
  }
}

export const redisCacheService = new RedisCacheService();
```

## Cache Invalidation Strategies

### 1. Time-Based (TTL)

```typescript
// Simple TTL - data expires automatically
await cacheService.set('config', configData, 3600); // 1 hour
```

### 2. Event-Based

```typescript
// Invalidate on data changes
class OrderService {
  async createOrder(data: CreateOrderDTO) {
    const order = await Order.create(data);

    // Invalidate related caches
    await Promise.all([
      cacheService.invalidate(`user:${data.userId}:orders`),
      cacheService.invalidate(`user:${data.userId}:stats`),
      cacheService.invalidatePattern(`orders:recent:*`),
    ]);

    return order;
  }
}
```

### 3. Publish/Subscribe for Distributed Cache

```typescript
// When running multiple instances
import redis from '../config/redis';

const subscriber = redis.duplicate();

// Publisher
async function invalidateAcrossInstances(pattern: string) {
  await redis.publish('cache:invalidate', JSON.stringify({ pattern }));
}

// Subscriber
subscriber.subscribe('cache:invalidate');
subscriber.on('message', (channel, message) => {
  if (channel === 'cache:invalidate') {
    const { pattern } = JSON.parse(message);
    localCache.invalidatePattern(pattern);
  }
});
```

## Caching Strategies by Data Type

### 1. Static Data (Config, Categories)

```typescript
// Long TTL, infrequent invalidation
const STATIC_TTL = 3600 * 24; // 24 hours

async function getCategories() {
  return cacheService.getOrSet(
    'categories:all',
    () => Category.find().lean(),
    STATIC_TTL
  );
}
```

### 2. User-Specific Data

```typescript
// Shorter TTL, scoped keys
const USER_DATA_TTL = 300; // 5 minutes

async function getUserDashboard(userId: string) {
  return cacheService.getOrSet(
    `user:${userId}:dashboard`,
    () => buildUserDashboard(userId),
    USER_DATA_TTL
  );
}
```

### 3. Frequently Changing Data

```typescript
// Very short TTL or no cache
const VOLATILE_TTL = 30; // 30 seconds

async function getRealtimeStats() {
  return cacheService.getOrSet(
    'stats:realtime',
    () => calculateRealtimeStats(),
    VOLATILE_TTL
  );
}
```

### 4. Aggregated Data

```typescript
// Pre-compute and cache expensive aggregations
async function getDailySalesReport(date: string) {
  return cacheService.getOrSet(
    `reports:sales:${date}`,
    async () => {
      const report = await Order.aggregate([
        { $match: { date: new Date(date) } },
        { $group: { /* ... */ } },
      ]);
      return report;
    },
    3600 * 12 // 12 hours
  );
}
```

## Cache-Aside Pattern

```typescript
async function getProduct(productId: string): Promise<Product | null> {
  // 1. Try cache
  const cached = await cacheService.get<Product>(`product:${productId}`);
  if (cached) return cached;

  // 2. Cache miss - fetch from DB
  const product = await Product.findById(productId).lean();

  // 3. Store in cache (even if null, to prevent repeated DB hits)
  if (product) {
    await cacheService.set(`product:${productId}`, product, 300);
  } else {
    // Cache null result with shorter TTL
    await cacheService.set(`product:${productId}`, null, 60);
  }

  return product;
}
```

## Write-Through Pattern

```typescript
async function updateProduct(productId: string, data: UpdateProductDTO) {
  // 1. Update DB
  const product = await Product.findByIdAndUpdate(productId, data, { new: true });

  // 2. Update cache immediately
  if (product) {
    await cacheService.set(`product:${productId}`, product, 300);
  }

  return product;
}
```

## Cache Performance Tips

| Tip | Why |
|-----|-----|
| Use `.lean()` in Mongoose | Returns plain objects, faster serialization |
| Compress large values | Reduce memory/network usage |
| Use hash types for objects | More efficient than JSON in Redis |
| Set appropriate TTLs | Balance freshness vs performance |
| Monitor hit rates | Tune cache size and TTL accordingly |

## Monitoring Cache Health

```typescript
class CacheMonitor {
  private hits = 0;
  private misses = 0;

  recordHit() { this.hits++; }
  recordMiss() { this.misses++; }

  getStats() {
    const total = this.hits + this.misses;
    return {
      hits: this.hits,
      misses: this.misses,
      hitRate: total > 0 ? this.hits / total : 0,
    };
  }

  reset() {
    this.hits = 0;
    this.misses = 0;
  }
}

export const cacheMonitor = new CacheMonitor();

// In cache service
async getOrSet<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const cached = this.cache.get(key);
  if (cached !== undefined) {
    cacheMonitor.recordHit();
    return cached as T;
  }

  cacheMonitor.recordMiss();
  const value = await fetcher();
  this.cache.set(key, value);
  return value;
}

// Expose stats endpoint
router.get('/admin/cache-stats', (req, res) => {
  res.json(cacheMonitor.getStats());
});
```
