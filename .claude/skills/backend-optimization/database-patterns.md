# Database Patterns - api

## MongoDB Optimization

### 1. Strategic Indexes

```typescript
// Create indexes on frequently queried fields
// In your model or migration
UserSchema.index({ email: 1 }, { unique: true });
UserSchema.index({ status: 1, createdAt: -1 }); // Compound index
UserSchema.index({ 'address.city': 1 }); // Nested field
UserSchema.index({ tags: 1 }); // Array field

// Text index for search
ProductSchema.index({ name: 'text', description: 'text' });

// TTL index for auto-deletion
SessionSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });
```

### When to Create Indexes

| Query Pattern | Index Type |
|--------------|------------|
| `find({ email: 'x' })` | Single field: `{ email: 1 }` |
| `find({ status: 'x' }).sort({ date: -1 })` | Compound: `{ status: 1, date: -1 }` |
| `find({ $text: { $search: 'x' } })` | Text index |
| Array contains | `{ tags: 1 }` |
| Geospatial | `{ location: '2dsphere' }` |

### 2. Projection (Select Only Needed Fields)

```typescript
// BAD - Returns all fields
const users = await User.find({ isActive: true });

// GOOD - Only needed fields
const users = await User.find(
  { isActive: true },
  { _id: 1, name: 1, email: 1, avatar: 1 }
);

// Alternative syntax
const users = await User.find({ isActive: true })
  .select('_id name email avatar');

// Exclude specific fields
const users = await User.find({ isActive: true })
  .select('-password -internalNotes');
```

### 3. Avoid N+1 Queries

```typescript
// BAD - N+1 queries
async function getOrdersWithProducts(userId: string) {
  const orders = await Order.find({ userId });
  return Promise.all(
    orders.map(async order => ({
      ...order.toObject(),
      // Each iteration makes a DB call!
      products: await Product.find({ _id: { $in: order.productIds } }),
    }))
  );
}

// GOOD - Single query with $lookup
async function getOrdersWithProducts(userId: string) {
  return Order.aggregate([
    { $match: { userId } },
    {
      $lookup: {
        from: 'products',
        localField: 'productIds',
        foreignField: '_id',
        as: 'products',
      },
    },
  ]);
}

// GOOD - Alternative: Fetch all products at once
async function getOrdersWithProducts(userId: string) {
  const orders = await Order.find({ userId });

  // Collect all product IDs
  const allProductIds = [...new Set(orders.flatMap(o => o.productIds))];

  // Single query for all products
  const products = await Product.find({ _id: { $in: allProductIds } });
  const productMap = new Map(products.map(p => [p._id.toString(), p]));

  return orders.map(order => ({
    ...order.toObject(),
    products: order.productIds.map(id => productMap.get(id.toString())),
  }));
}
```

### 4. Aggregation Pipeline

```typescript
// Complex queries should use aggregation
async function getOrderStats(userId: string, startDate: Date) {
  return Order.aggregate([
    // Stage 1: Filter
    {
      $match: {
        userId,
        createdAt: { $gte: startDate },
        status: { $in: ['completed', 'shipped'] },
      },
    },
    // Stage 2: Group
    {
      $group: {
        _id: { $dateToString: { format: '%Y-%m', date: '$createdAt' } },
        totalOrders: { $sum: 1 },
        totalRevenue: { $sum: '$total' },
        avgOrderValue: { $avg: '$total' },
      },
    },
    // Stage 3: Sort
    { $sort: { _id: -1 } },
    // Stage 4: Limit
    { $limit: 12 },
  ]);
}
```

### 5. Pagination

```typescript
// Offset pagination (simple but slow for large offsets)
async function getUsers(page: number, limit: number) {
  const skip = (page - 1) * limit;
  const [users, total] = await Promise.all([
    User.find().skip(skip).limit(limit),
    User.countDocuments(),
  ]);
  return { users, total, page, totalPages: Math.ceil(total / limit) };
}

// Cursor pagination (faster for large datasets)
async function getUsersCursor(cursor: string | null, limit: number) {
  const query = cursor
    ? { _id: { $gt: new ObjectId(cursor) } }
    : {};

  const users = await User.find(query)
    .sort({ _id: 1 })
    .limit(limit + 1);

  const hasMore = users.length > limit;
  const items = hasMore ? users.slice(0, -1) : users;
  const nextCursor = hasMore ? items[items.length - 1]._id : null;

  return { users: items, nextCursor, hasMore };
}
```

## Firestore Patterns

### 1. Batch Operations

```typescript
// BAD - Individual writes
async function updateUsers(updates: UserUpdate[]) {
  for (const update of updates) {
    await firestore.collection('users').doc(update.id).update(update.data);
  }
}

// GOOD - Batch write (max 500 operations per batch)
async function updateUsers(updates: UserUpdate[]) {
  const batches = chunk(updates, 500);

  for (const batch of batches) {
    const writeBatch = firestore.batch();

    for (const update of batch) {
      const ref = firestore.collection('users').doc(update.id);
      writeBatch.update(ref, update.data);
    }

    await writeBatch.commit();
  }
}
```

### 2. Parallel Batches

```typescript
// Process multiple batches in parallel
async function updateUsersParallel(updates: UserUpdate[]) {
  const batches = chunk(updates, 500);

  await Promise.all(
    batches.map(async batch => {
      const writeBatch = firestore.batch();
      batch.forEach(update => {
        const ref = firestore.collection('users').doc(update.id);
        writeBatch.update(ref, update.data);
      });
      await writeBatch.commit();
    })
  );
}
```

### 3. Read Optimization

```typescript
// Use getAll for multiple documents
async function getUsers(userIds: string[]) {
  const refs = userIds.map(id => firestore.collection('users').doc(id));
  const snapshots = await firestore.getAll(...refs);
  return snapshots.map(snap => snap.data());
}

// Select specific fields
async function getUserNames(userIds: string[]) {
  const refs = userIds.map(id => firestore.collection('users').doc(id));
  const snapshots = await firestore.getAll(...refs);
  return snapshots.map(snap => ({
    id: snap.id,
    name: snap.get('name'),
  }));
}
```

## Connection Management

### 1. MongoDB Connection Pool

```typescript
// config/database.ts
import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI!;

const options: mongoose.ConnectOptions = {
  maxPoolSize: 10, // Default is 5
  minPoolSize: 2,
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
  family: 4, // Use IPv4
};

export async function connectDB() {
  try {
    await mongoose.connect(MONGODB_URI, options);
    console.log('MongoDB connected');
  } catch (error) {
    console.error('MongoDB connection error:', error);
    process.exit(1);
  }
}

// Monitor connection
mongoose.connection.on('error', err => {
  console.error('MongoDB error:', err);
});

mongoose.connection.on('disconnected', () => {
  console.warn('MongoDB disconnected');
});
```

### 2. Graceful Shutdown

```typescript
// server.ts
process.on('SIGINT', async () => {
  console.log('Shutting down gracefully...');

  // Close MongoDB connection
  await mongoose.connection.close();

  // Close Express server
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
```

## Query Optimization Checklist

| Check | Command |
|-------|---------|
| Explain query | `Model.find({...}).explain('executionStats')` |
| Check indexes | `db.collection.getIndexes()` |
| Find slow queries | Enable MongoDB profiler |
| Memory usage | `db.serverStatus().mem` |

### Explain Output

```typescript
const stats = await User.find({ status: 'active' })
  .sort({ createdAt: -1 })
  .explain('executionStats');

// Look for these in output:
// - totalDocsExamined should be close to nReturned
// - stage: "IXSCAN" (good) vs "COLLSCAN" (bad)
// - executionTimeMillis should be low
```

## Common Query Patterns

### 1. Upsert

```typescript
const user = await User.findOneAndUpdate(
  { email },
  { $set: { lastLogin: new Date() }, $setOnInsert: { createdAt: new Date() } },
  { upsert: true, new: true }
);
```

### 2. Atomic Increment

```typescript
await Product.findByIdAndUpdate(productId, {
  $inc: { viewCount: 1, stockQuantity: -1 },
});
```

### 3. Array Operations

```typescript
// Add to array (if not exists)
await User.findByIdAndUpdate(userId, {
  $addToSet: { favorites: productId },
});

// Remove from array
await User.findByIdAndUpdate(userId, {
  $pull: { favorites: productId },
});

// Update array element
await User.updateOne(
  { _id: userId, 'addresses._id': addressId },
  { $set: { 'addresses.$.isDefault': true } }
);
```
