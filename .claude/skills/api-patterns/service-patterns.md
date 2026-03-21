# Service Patterns for api

Business logic layer.

---

## Basic Service

```typescript
// src/services/ProductService.ts
import { productRepository } from '../repositories'
import { NotFoundError, ValidationError } from '../errors'

export class ProductService {
  async create(data: CreateProductInput, aid: string) {
    // Business validation
    await this.validateProduct(data)

    // Create product
    return await productRepository.create({ ...data, aid })
  }

  async findByAid(aid: string) {
    return await productRepository.findByAid(aid)
  }

  async findById(id: string, aid: string) {
    const product = await productRepository.findById(id)

    if (!product) {
      throw new NotFoundError('Product not found')
    }

    // Authorization check
    if (product.aid !== aid) {
      throw new UnauthorizedError('Access denied')
    }

    return product
  }

  async update(id: string, data: UpdateProductInput, aid: string) {
    // Check existence and authorization
    await this.findById(id, aid)

    // Update
    return await productRepository.update(id, data)
  }

  async delete(id: string, aid: string) {
    // Check existence and authorization
    await this.findById(id, aid)

    // Delete
    await productRepository.delete(id)
  }

  private async validateProduct(data: CreateProductInput) {
    // Check for duplicates
    const existing = await productRepository.findByName(data.name)
    if (existing) {
      throw new ValidationError('Product name already exists')
    }

    // Business rules
    if (data.price < 0) {
      throw new ValidationError('Price must be positive')
    }
  }
}

export const productService = new ProductService()
```

---

## Parallel Data Fetching

```typescript
async getDashboard(userId: string) {
  // BAD - Sequential (slow)
  const user = await userRepository.findById(userId)
  const orders = await orderRepository.findByUserId(userId)
  const products = await productRepository.findByUserId(userId)

  // GOOD - Parallel (fast)
  const [user, orders, products] = await Promise.all([
    userRepository.findById(userId),
    orderRepository.findByUserId(userId),
    productRepository.findByUserId(userId),
  ])

  return { user, orders, products }
}
```

---

## Transaction Management

```typescript
import mongoose from 'mongoose'

async transferInventory(fromId: string, toId: string, quantity: number) {
  const session = await mongoose.startSession()
  session.startTransaction()

  try {
    // Deduct from source
    await inventoryRepository.decrement(fromId, quantity, { session })

    // Add to destination
    await inventoryRepository.increment(toId, quantity, { session })

    await session.commitTransaction()
  } catch (error) {
    await session.abortTransaction()
    throw error
  } finally {
    session.endSession()
  }
}
```
