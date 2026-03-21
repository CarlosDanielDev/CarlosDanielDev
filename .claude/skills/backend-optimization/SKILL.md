---
name: backend-optimization
version: "1.0.0"
description: Optimize Express.js API performance in api. Use when improving MongoDB queries, implementing caching, parallel data fetching, Zod validation, or optimizing service/repository patterns.
allowed-tools: Read, Grep, Glob, WebSearch
---

# Backend Optimization

Performance optimization patterns for Express.js APIs in api.

## Skill Usage

| Aspect | Details |
|--------|---------|
| **Consumer** | `subagent-backend-architect` |
| **Purpose** | Consulted during backend architecture analysis and implementation planning |
| **Invocation** | Subagents read this skill; NOT directly invocable by users |
| **Related Skills** | `shared-patterns` (TypeScript/async patterns) |

## Critical Stack Requirements

| Feature | Pattern | Notes |
|---------|---------|-------|
| Framework | Express.js | REST APIs |
| Database | MongoDB + Firestore | Primary + sync |
| Validation | Zod schemas | Request/response |
| Architecture | Service/Repository | Clean separation |

## Quick Performance Wins

### 1. Use MongoDB Projection

```typescript
// BAD - Fetches all fields
const users = await User.find({ status: 'active' });

// GOOD - Only needed fields
const users = await User.find(
  { status: 'active' },
  { _id: 1, name: 1, email: 1 }
);
```

### 2. Parallel Data Fetching

```typescript
// BAD - Sequential (slower)
const user = await getUser(userId);
const orders = await getOrders(userId);
const notifications = await getNotifications(userId);

// GOOD - Parallel (faster)
const [user, orders, notifications] = await Promise.all([
  getUser(userId),
  getOrders(userId),
  getNotifications(userId),
]);
```

### 3. Early Return Pattern

```typescript
// BAD - Nested conditions
async function processOrder(orderId: string) {
  const order = await Order.findById(orderId);
  if (order) {
    if (order.status === 'pending') {
      if (order.items.length > 0) {
        // Process...
      }
    }
  }
}

// GOOD - Early returns
async function processOrder(orderId: string) {
  const order = await Order.findById(orderId);
  if (!order) return null;
  if (order.status !== 'pending') return null;
  if (order.items.length === 0) return null;

  // Process...
}
```

## Detailed Guides

- [Database Patterns](database-patterns.md) - MongoDB, indexes, aggregation
- [API Performance](api-performance.md) - Parallel fetching, streaming, compression
- [Caching](caching.md) - LRU, Redis, invalidation strategies

## Key Anti-Patterns

1. N+1 queries (loop with DB calls)
2. Missing indexes on filtered/sorted fields
3. Sequential `await` for independent operations
4. Fetching full documents when only few fields needed
5. Synchronous Zod parsing for large payloads
