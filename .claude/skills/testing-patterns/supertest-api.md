# Supertest API Testing for api

Backend API testing with Supertest and Jest.

---

## Test Setup

```typescript
// tests/setup.ts
import { MongoMemoryServer } from 'mongodb-memory-server'
import mongoose from 'mongoose'

let mongoServer: MongoMemoryServer

beforeAll(async () => {
  mongoServer = await MongoMemoryServer.create()
  await mongoose.connect(mongoServer.getUri())
})

afterAll(async () => {
  await mongoose.disconnect()
  await mongoServer.stop()
})

afterEach(async () => {
  const collections = mongoose.connection.collections
  for (const key in collections) {
    await collections[key].deleteMany({})
  }
})
```

---

## Basic API Test

```typescript
// tests/api/products.test.ts
import request from 'supertest'
import app from '../../src/app'

describe('POST /api/products', () => {
  it('should create a product', async () => {
    const response = await request(app)
      .post('/api/products')
      .send({
        name: 'Test Product',
        price: 29.99,
        description: 'A test product',
      })
      .expect(201)

    expect(response.body).toMatchObject({
      name: 'Test Product',
      price: 29.99,
    })
    expect(response.body._id).toBeDefined()
  })

  it('should validate required fields', async () => {
    const response = await request(app)
      .post('/api/products')
      .send({ price: 29.99 })
      .expect(400)

    expect(response.body.error).toContain('name')
  })
})
```

---

## Authentication Tests

```typescript
describe('Protected Routes', () => {
  let authToken: string

  beforeEach(async () => {
    // Create user and get token
    await request(app)
      .post('/api/auth/register')
      .send({
        email: 'test@example.com',
        password: 'password123',
      })

    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'password123',
      })

    authToken = loginResponse.body.token
  })

  it('should require authentication', async () => {
    await request(app)
      .get('/api/products')
      .expect(401)
  })

  it('should allow authenticated requests', async () => {
    await request(app)
      .get('/api/products')
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200)
  })
})
```

---

## CRUD Tests

```typescript
describe('Product CRUD', () => {
  let productId: string

  beforeEach(async () => {
    const response = await request(app)
      .post('/api/products')
      .send({ name: 'Test Product', price: 29.99 })
      .expect(201)

    productId = response.body._id
  })

  it('should get all products', async () => {
    const response = await request(app)
      .get('/api/products')
      .expect(200)

    expect(response.body).toHaveLength(1)
    expect(response.body[0].name).toBe('Test Product')
  })

  it('should get product by id', async () => {
    const response = await request(app)
      .get(`/api/products/${productId}`)
      .expect(200)

    expect(response.body.name).toBe('Test Product')
  })

  it('should update product', async () => {
    const response = await request(app)
      .put(`/api/products/${productId}`)
      .send({ name: 'Updated Product' })
      .expect(200)

    expect(response.body.name).toBe('Updated Product')
  })

  it('should delete product', async () => {
    await request(app)
      .delete(`/api/products/${productId}`)
      .expect(204)

    await request(app)
      .get(`/api/products/${productId}`)
      .expect(404)
  })
})
```

---

## Error Handling Tests

```typescript
describe('Error Handling', () => {
  it('should return 404 for non-existent resource', async () => {
    await request(app)
      .get('/api/products/507f1f77bcf86cd799439011')
      .expect(404)
  })

  it('should return 400 for invalid id format', async () => {
    await request(app)
      .get('/api/products/invalid-id')
      .expect(400)
  })

  it('should handle validation errors', async () => {
    const response = await request(app)
      .post('/api/products')
      .send({ price: 'invalid' })
      .expect(400)

    expect(response.body.errors).toBeDefined()
  })
})
```

---

## Zod Validation Tests

```typescript
import { z } from 'zod'

const ProductSchema = z.object({
  name: z.string().min(1),
  price: z.number().positive(),
  description: z.string().optional(),
})

it('should validate with Zod schema', async () => {
  const validProduct = { name: 'Product', price: 29.99 }
  expect(() => ProductSchema.parse(validProduct)).not.toThrow()

  const invalidProduct = { name: '', price: -10 }
  expect(() => ProductSchema.parse(invalidProduct)).toThrow()
})
```

---

## Test Factories

```typescript
// tests/factories/productFactory.ts
export const createProduct = async (overrides = {}) => {
  const product = {
    name: 'Test Product',
    price: 29.99,
    description: 'Test description',
    ...overrides,
  }

  const response = await request(app)
    .post('/api/products')
    .send(product)

  return response.body
}

// Usage
it('should test with factory', async () => {
  const product = await createProduct({ name: 'Custom Name' })
  expect(product.name).toBe('Custom Name')
})
```

---

## Integration Tests

```typescript
describe('Service Integration', () => {
  it('should integrate service and repository layers', async () => {
    // Test full flow from controller -> service -> repository -> DB
    const response = await request(app)
      .post('/api/products')
      .send({ name: 'Integration Test', price: 49.99 })
      .expect(201)

    // Verify in database
    const product = await Product.findById(response.body._id)
    expect(product).toBeDefined()
    expect(product.name).toBe('Integration Test')
  })
})
```

---

## Commands Reference

```bash
# Run all tests
yarn test

# Run specific test file
yarn test tests/api/products.test.ts

# Run with coverage
yarn test:coverage

# Watch mode
yarn test:watch

# Integration tests only
yarn test:integration
```
