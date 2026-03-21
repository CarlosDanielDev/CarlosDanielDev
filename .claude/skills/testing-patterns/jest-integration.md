# Jest Integration Testing

Integration testing patterns for api.

---

## Service Layer Testing

```typescript
// tests/services/productService.test.ts
import { ProductService } from '../../src/services/ProductService'
import { ProductRepository } from '../../src/repositories/ProductRepository'

describe('ProductService', () => {
  let service: ProductService
  let repository: ProductRepository

  beforeEach(() => {
    repository = new ProductRepository()
    service = new ProductService(repository)
  })

  it('should create product', async () => {
    const product = await service.createProduct({
      name: 'Test Product',
      price: 29.99,
    })

    expect(product).toBeDefined()
    expect(product.name).toBe('Test Product')
  })

  it('should validate product data', async () => {
    await expect(
      service.createProduct({ name: '', price: -10 })
    ).rejects.toThrow('Invalid product data')
  })
})
```

---

## Repository Pattern Testing

```typescript
// tests/repositories/productRepository.test.ts
import { ProductRepository } from '../../src/repositories/ProductRepository'
import { Product } from '../../src/models/Product'

describe('ProductRepository', () => {
  let repository: ProductRepository

  beforeEach(() => {
    repository = new ProductRepository()
  })

  it('should find all products', async () => {
    await Product.create({ name: 'Product 1', price: 10 })
    await Product.create({ name: 'Product 2', price: 20 })

    const products = await repository.findAll()
    expect(products).toHaveLength(2)
  })

  it('should find product by id', async () => {
    const created = await Product.create({ name: 'Product', price: 10 })
    const found = await repository.findById(created._id)

    expect(found?.name).toBe('Product')
  })
})
```

---

## MongoDB Memory Server

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
