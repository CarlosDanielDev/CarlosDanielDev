# Repository Patterns for api

Data access layer for MongoDB and Firestore.

---

## Basic Repository

```typescript
// src/repositories/ProductRepository.ts
import { Product } from '../models/Product'

export class ProductRepository {
  async create(data: ProductInput) {
    return await Product.create(data)
  }

  async findById(id: string) {
    return await Product.findById(id)
  }

  async findByAid(aid: string) {
    return await Product.find({ aid }).select('name price description -_id')
  }

  async update(id: string, data: Partial<ProductInput>) {
    return await Product.findByIdAndUpdate(id, data, { new: true })
  }

  async delete(id: string) {
    return await Product.findByIdAndDelete(id)
  }
}

export const productRepository = new ProductRepository()
```

---

## Query Optimization

```typescript
// BAD - Fetches all fields
async findProducts(aid: string) {
  return await Product.find({ aid })
}

// GOOD - Projection (only needed fields)
async findProducts(aid: string) {
  return await Product.find({ aid }).select('name price -_id')
}

// GOOD - Lean (plain objects, faster)
async findProducts(aid: string) {
  return await Product.find({ aid }).select('name price').lean()
}
```

---

## Indexes

```typescript
// src/models/Product.ts
import mongoose from 'mongoose'

const productSchema = new mongoose.Schema({
  name: { type: String, required: true },
  aid: { type: String, required: true },
  price: { type: Number, required: true },
  status: { type: String, enum: ['active', 'inactive'], default: 'active' },
  createdAt: { type: Date, default: Date.now }
})

// Indexes for common queries
productSchema.index({ aid: 1 })
productSchema.index({ aid: 1, status: 1 })
productSchema.index({ createdAt: -1 })

export const Product = mongoose.model('Product', productSchema)
```

---

## Aggregation Pipeline

```typescript
async getProductStats(aid: string) {
  return await Product.aggregate([
    { $match: { aid } },
    {
      $group: {
        _id: '$category',
        count: { $sum: 1 },
        avgPrice: { $avg: '$price' },
        totalRevenue: { $sum: { $multiply: ['$price', '$quantity'] } }
      }
    },
    { $sort: { totalRevenue: -1 } }
  ])
}
```

---

## Pagination

```typescript
async findPaginated(aid: string, page: number = 1, limit: number = 20) {
  const skip = (page - 1) * limit

  const [data, total] = await Promise.all([
    Product.find({ aid })
      .skip(skip)
      .limit(limit)
      .sort({ createdAt: -1 })
      .lean(),
    Product.countDocuments({ aid })
  ])

  return {
    data,
    meta: {
      page,
      limit,
      total,
      pages: Math.ceil(total / limit)
    }
  }
}
```

---

## Firestore Sync

```typescript
import { Firestore } from '@google-cloud/firestore'

const firestore = new Firestore()

async create(data: ProductInput) {
  // Create in MongoDB
  const product = await Product.create(data)

  // Sync to Firestore
  await firestore.collection('products').doc(product.id).set({
    name: product.name,
    price: product.price,
    aid: product.aid,
    syncedAt: new Date()
  })

  return product
}
```
