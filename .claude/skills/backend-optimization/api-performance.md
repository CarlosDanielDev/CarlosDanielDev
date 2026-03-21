# API Performance - api

## Parallel Data Fetching

### 1. Promise.all for Independent Operations

```typescript
// BAD - Sequential (total: 200 + 150 + 100 = 450ms)
async function getDashboard(userId: string) {
  const user = await userService.getUser(userId);      // 200ms
  const orders = await orderService.getOrders(userId); // 150ms
  const stats = await statsService.getStats(userId);   // 100ms
  return { user, orders, stats };
}

// GOOD - Parallel (total: max(200, 150, 100) = 200ms)
async function getDashboard(userId: string) {
  const [user, orders, stats] = await Promise.all([
    userService.getUser(userId),
    orderService.getOrders(userId),
    statsService.getStats(userId),
  ]);
  return { user, orders, stats };
}
```

### 2. Promise.allSettled for Partial Failures

```typescript
// When some data is optional and failures are acceptable
async function getEnrichedProfile(userId: string) {
  const results = await Promise.allSettled([
    userService.getUser(userId),         // Required
    socialService.getSocialLinks(userId), // Optional
    analyticsService.getActivity(userId), // Optional
  ]);

  const [userResult, socialResult, activityResult] = results;

  // User is required
  if (userResult.status === 'rejected') {
    throw userResult.reason;
  }

  return {
    user: userResult.value,
    social: socialResult.status === 'fulfilled' ? socialResult.value : null,
    activity: activityResult.status === 'fulfilled' ? activityResult.value : null,
  };
}
```

### 3. Concurrent with Limit

```typescript
// Process many items with concurrency control
import pLimit from 'p-limit';

async function processOrders(orderIds: string[]) {
  const limit = pLimit(5); // Max 5 concurrent

  return Promise.all(
    orderIds.map(id => limit(() => processOrder(id)))
  );
}
```

## Early Return Pattern

### 1. Guard Clauses

```typescript
// BAD - Deep nesting
async function processPayment(orderId: string) {
  const order = await Order.findById(orderId);
  if (order) {
    if (order.status === 'pending') {
      const user = await User.findById(order.userId);
      if (user) {
        if (user.paymentMethod) {
          // Finally process...
          return await chargeUser(user, order.total);
        } else {
          throw new Error('No payment method');
        }
      } else {
        throw new Error('User not found');
      }
    } else {
      throw new Error('Order not pending');
    }
  } else {
    throw new Error('Order not found');
  }
}

// GOOD - Guard clauses
async function processPayment(orderId: string) {
  const order = await Order.findById(orderId);
  if (!order) throw new NotFoundError('Order not found');
  if (order.status !== 'pending') throw new BadRequestError('Order not pending');

  const user = await User.findById(order.userId);
  if (!user) throw new NotFoundError('User not found');
  if (!user.paymentMethod) throw new BadRequestError('No payment method');

  return chargeUser(user, order.total);
}
```

### 2. Fast Validation Failures

```typescript
// Validate early, fail fast
async function createOrder(data: CreateOrderDTO) {
  // 1. Validate input (no DB calls yet)
  const validation = createOrderSchema.safeParse(data);
  if (!validation.success) {
    throw new ValidationError(validation.error);
  }

  // 2. Check user exists (cheap query)
  const userExists = await User.exists({ _id: data.userId });
  if (!userExists) {
    throw new NotFoundError('User not found');
  }

  // 3. Check product availability (may be expensive)
  const products = await Product.find({
    _id: { $in: data.productIds },
    stock: { $gt: 0 },
  });
  if (products.length !== data.productIds.length) {
    throw new BadRequestError('Some products unavailable');
  }

  // 4. Create order (expensive operation last)
  return Order.create(validation.data);
}
```

## Streaming Responses

### 1. Large JSON Responses

```typescript
import { Readable } from 'stream';

// For very large datasets
router.get('/export/users', async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.write('[');

  let first = true;
  const cursor = User.find().cursor();

  for await (const user of cursor) {
    if (!first) res.write(',');
    res.write(JSON.stringify(user));
    first = false;
  }

  res.write(']');
  res.end();
});
```

### 2. CSV Export

```typescript
import { stringify } from 'csv-stringify';

router.get('/export/orders.csv', async (req, res) => {
  res.setHeader('Content-Type', 'text/csv');
  res.setHeader('Content-Disposition', 'attachment; filename="orders.csv"');

  const stringifier = stringify({
    header: true,
    columns: ['id', 'customer', 'total', 'status', 'date'],
  });

  stringifier.pipe(res);

  const cursor = Order.find().cursor();
  for await (const order of cursor) {
    stringifier.write({
      id: order._id,
      customer: order.customerName,
      total: order.total,
      status: order.status,
      date: order.createdAt.toISOString(),
    });
  }

  stringifier.end();
});
```

## Compression

### 1. Enable Compression Middleware

```typescript
import compression from 'compression';

// Compress all responses > 1KB
app.use(compression({
  threshold: 1024,
  level: 6, // Compression level (1-9)
  filter: (req, res) => {
    // Don't compress if client doesn't accept it
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  },
}));
```

### 2. Selective Compression

```typescript
// Only compress specific routes
const compressMiddleware = compression({ threshold: 0 });

router.get('/api/large-data', compressMiddleware, async (req, res) => {
  const data = await getLargeDataset();
  res.json(data);
});
```

## Zod Validation Optimization

### 1. Lazy Parsing for Large Payloads

```typescript
// Defer parsing until needed
const largeSchema = z.lazy(() => z.object({
  items: z.array(itemSchema).max(1000),
  // ... other fields
}));
```

### 2. Async Refinements

```typescript
// Expensive validations run async
const userSchema = z.object({
  email: z.string().email(),
  username: z.string().min(3),
}).refine(
  async (data) => {
    // Check uniqueness in parallel
    const [emailExists, usernameExists] = await Promise.all([
      User.exists({ email: data.email }),
      User.exists({ username: data.username }),
    ]);
    return !emailExists && !usernameExists;
  },
  { message: 'Email or username already exists' }
);
```

### 3. Precompiled Schemas

```typescript
// Compile schemas at startup, not per request
const schemas = {
  createUser: z.object({ /* ... */ }),
  updateUser: z.object({ /* ... */ }),
  createOrder: z.object({ /* ... */ }),
};

// Use in middleware
const validate = (schemaName: keyof typeof schemas) => (req, res, next) => {
  const result = schemas[schemaName].safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.issues });
  }
  req.validated = result.data;
  next();
};
```

## Response Optimization

### 1. Conditional Requests (ETag)

```typescript
import etag from 'etag';

router.get('/api/config', async (req, res) => {
  const config = await getConfig();
  const configStr = JSON.stringify(config);
  const hash = etag(configStr);

  // Check if client has current version
  if (req.headers['if-none-match'] === hash) {
    return res.status(304).end();
  }

  res.setHeader('ETag', hash);
  res.setHeader('Cache-Control', 'private, max-age=60');
  res.json(config);
});
```

### 2. Partial Responses

```typescript
// Allow clients to request specific fields
router.get('/api/users/:id', async (req, res) => {
  const fields = req.query.fields?.split(',') || [];

  const projection = fields.length > 0
    ? fields.reduce((acc, f) => ({ ...acc, [f]: 1 }), {})
    : undefined;

  const user = await User.findById(req.params.id, projection);
  res.json(user);
});

// Usage: GET /api/users/123?fields=name,email,avatar
```

### 3. Response Size Limits

```typescript
// Limit response size to prevent memory issues
router.get('/api/orders', async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 20, 100); // Max 100

  const orders = await Order.find()
    .sort({ createdAt: -1 })
    .limit(limit)
    .lean(); // Return plain objects (faster)

  res.json(orders);
});
```

## Async Error Handling

```typescript
// Wrapper for async route handlers
const asyncHandler = (fn: RequestHandler): RequestHandler => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

// Usage
router.get('/users/:id', asyncHandler(async (req, res) => {
  const user = await userService.getUser(req.params.id);
  if (!user) throw new NotFoundError('User not found');
  res.json(user);
}));

// Error middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof NotFoundError) {
    return res.status(404).json({ error: err.message });
  }
  if (err instanceof ValidationError) {
    return res.status(400).json({ errors: err.issues });
  }
  console.error(err);
  res.status(500).json({ error: 'Internal server error' });
});
```

## Request Logging

```typescript
import morgan from 'morgan';

// Log slow requests
const slowRequestThreshold = 1000; // 1 second

app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    if (duration > slowRequestThreshold) {
      console.warn(`Slow request: ${req.method} ${req.path} - ${duration}ms`);
    }
  });
  next();
});

// Development logging
if (process.env.NODE_ENV === 'development') {
  app.use(morgan('dev'));
}
```
