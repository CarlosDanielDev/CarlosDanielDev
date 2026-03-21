---
name: shared-patterns
version: "1.0.0"
description: Shared TypeScript and async patterns for all platforms. Use when improving code quality, handling async operations, error handling, or applying TypeScript best practices across mobile-app, web-app, or api.
allowed-tools: Read, Grep, Glob, WebSearch
---

# Shared Patterns

Cross-platform optimization patterns for TypeScript and async operations used across all applications.

## Skill Usage

| Aspect | Details |
|--------|---------|
| **Consumer** | All architect subagents (`mobile`, `frontend`, `backend`) |
| **Purpose** | Consulted for TypeScript best practices and async patterns |
| **Invocation** | Subagents read this skill; NOT directly invocable by users |
| **Related Skills** | Platform-specific skills (`mobile-optimization`, `web-app-optimization`, `backend-optimization`) |

## Applies To

- **mobile-app** (React Native)
- **web-app** (React Web)
- **api** (Express.js backend)

## Quick Reference

### TypeScript Essentials

```typescript
// Prefer type narrowing over casting
function processUser(user: User | null) {
  if (!user) return null;
  // user is now User (narrowed)
  return user.name;
}

// Use discriminated unions for state
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };
```

### Async Essentials

```typescript
// Parallel fetching - use Promise.all for independent requests
const [users, products] = await Promise.all([
  fetchUsers(),
  fetchProducts()
]);

// Use Promise.allSettled when some failures are acceptable
const results = await Promise.allSettled([
  fetchUser(1),
  fetchUser(2),
  fetchUser(3)
]);
```

## Detailed Guides

- [TypeScript Best Practices](typescript-best-practices.md) - Type safety, narrowing, generics
- [Async Patterns](async-patterns.md) - Parallel fetching, cancellation, retry logic

## Anti-Patterns to Avoid

1. **Sequential awaits** when requests are independent
2. **any** type instead of proper typing
3. **Type assertions** (`as Type`) without validation
4. **Nested try-catch** instead of error boundaries
5. **Unhandled promise rejections**
