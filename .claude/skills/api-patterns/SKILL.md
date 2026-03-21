---
name: api-patterns
version: "1.0.0"
description: Express.js API patterns for api including controllers, services, repositories, Zod validation, and MongoDB operations. Use when designing backend architecture or implementing APIs.
allowed-tools: Read, Grep, Glob, WebSearch
---

# API Patterns (api)

Backend architecture patterns for Express.js APIs.

## Skill Usage

| Aspect | Details |
|--------|---------|
| **Consumer** | `subagent-backend-architect` |
| **Purpose** | Backend implementation patterns and architecture |
| **Invocation** | Backend subagent reads this skill; NOT directly invocable by users |
| **Related Skills** | `backend-optimization`, `shared-patterns` |

---

## Critical Stack Requirements

| Layer | Pattern | Purpose |
|-------|---------|---------|
| **Controller** | Express route handlers | HTTP layer, request/response |
| **Service** | Business logic | Orchestration, validation |
| **Repository** | Data access | Database operations |
| **Validation** | Zod schemas | Input/output validation |
| **Database** | MongoDB + Firestore | Primary + sync |

---

## Quick Architecture Pattern

```
Request
  ↓
Controller (HTTP layer)
  ↓
Service (Business logic)
  ↓
Repository (Data access)
  ↓
Database
```

---

## Quick Patterns Reference

### Controller

```typescript
// src/controllers/productController.ts
export const createProduct = async (req: Request, res: Response) => {
  try {
    const data = CreateProductSchema.parse(req.body)
    const product = await productService.create(data, req.user.aid)
    res.status(201).json(product)
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ errors: error.errors })
    }
    res.status(500).json({ error: 'Internal server error' })
  }
}
```

### Service

```typescript
// src/services/ProductService.ts
export class ProductService {
  async create(data: CreateProductInput, aid: string) {
    // Validate business rules
    await this.validateProduct(data)

    // Create via repository
    return await productRepository.create({ ...data, aid })
  }
}
```

### Repository

```typescript
// src/repositories/ProductRepository.ts
export class ProductRepository {
  async create(data: ProductInput) {
    return await Product.create(data)
  }

  async findByAid(aid: string) {
    return await Product.find({ aid }).select('name price -_id')
  }
}
```

---

## Detailed API Guides

For comprehensive patterns, see:

- **[rest-api-patterns.md](rest-api-patterns.md)** - REST API design
  - Endpoint naming conventions
  - HTTP methods and status codes
  - Request/response patterns
  - Error handling

- **[controller-patterns.md](controller-patterns.md)** - Controller layer
  - Route handlers
  - Request validation
  - Response formatting
  - Error handling

- **[service-patterns.md](service-patterns.md)** - Service layer
  - Business logic orchestration
  - Transaction management
  - Inter-service communication
  - Caching strategies

- **[repository-patterns.md](repository-patterns.md)** - Data access
  - MongoDB operations
  - Query optimization
  - Aggregation pipelines
  - Firestore sync

- **[validation-patterns.md](validation-patterns.md)** - Zod validation
  - Schema definition
  - Request validation
  - Response validation
  - Custom validators

- **[auth-patterns.md](auth-patterns.md)** - Authentication
  - ValidateUID middleware
  - ValidateUserAID patterns
  - JWT handling
  - Role-based access

---

## Common Anti-Patterns to Avoid

1. ❌ Business logic in controllers
2. ❌ Direct database calls from controllers
3. ❌ Missing input validation
4. ❌ N+1 queries (loop with DB calls)
5. ❌ Sequential await for independent operations
6. ❌ Missing error handling
7. ❌ Verbose error messages to clients

---

## Key Dependencies

```json
{
  "express": "Web framework",
  "zod": "Validation",
  "mongoose": "MongoDB ODM",
  "@google-cloud/firestore": "Firestore",
  "jsonwebtoken": "JWT auth",
  "bcrypt": "Password hashing"
}
```

---

## When to Consult This Skill

- Designing REST API endpoints
- Implementing service/repository patterns
- Adding Zod validation
- Structuring backend architecture
- Optimizing database queries
- Implementing authentication
