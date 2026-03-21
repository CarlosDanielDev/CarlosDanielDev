# Controller Patterns for api

HTTP layer and request handling.

---

## Basic Controller

```typescript
// src/controllers/productController.ts
import { Request, Response } from 'express'
import { productService } from '../services'
import { CreateProductSchema } from '../validation/schemas'
import { z } from 'zod'

export const createProduct = async (req: Request, res: Response) => {
  try {
    // Validate input
    const data = CreateProductSchema.parse(req.body)

    // Call service
    const product = await productService.create(data, req.user.aid)

    // Return response
    res.status(201).json(product)
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ errors: error.errors })
    }
    res.status(500).json({ error: 'Internal server error' })
  }
}

export const getProducts = async (req: Request, res: Response) => {
  try {
    const products = await productService.findByAid(req.user.aid)
    res.json(products)
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' })
  }
}
```

---

## CRUD Controller Template

```typescript
export class ProductController {
  async create(req: Request, res: Response) {
    try {
      const data = CreateProductSchema.parse(req.body)
      const product = await productService.create(data, req.user.aid)
      res.status(201).json(product)
    } catch (error) {
      handleError(error, res)
    }
  }

  async findAll(req: Request, res: Response) {
    try {
      const products = await productService.findByAid(req.user.aid)
      res.json(products)
    } catch (error) {
      handleError(error, res)
    }
  }

  async findById(req: Request, res: Response) {
    try {
      const product = await productService.findById(req.params.id, req.user.aid)
      if (!product) {
        return res.status(404).json({ error: 'Product not found' })
      }
      res.json(product)
    } catch (error) {
      handleError(error, res)
    }
  }

  async update(req: Request, res: Response) {
    try {
      const data = UpdateProductSchema.parse(req.body)
      const product = await productService.update(req.params.id, data, req.user.aid)
      res.json(product)
    } catch (error) {
      handleError(error, res)
    }
  }

  async delete(req: Request, res: Response) {
    try {
      await productService.delete(req.params.id, req.user.aid)
      res.status(204).send()
    } catch (error) {
      handleError(error, res)
    }
  }
}
```

---

## Error Handling

```typescript
const handleError = (error: unknown, res: Response) => {
  if (error instanceof z.ZodError) {
    return res.status(400).json({
      error: 'Validation failed',
      details: error.errors
    })
  }

  if (error instanceof NotFoundError) {
    return res.status(404).json({ error: error.message })
  }

  if (error instanceof UnauthorizedError) {
    return res.status(403).json({ error: 'Forbidden' })
  }

  console.error(error)
  res.status(500).json({ error: 'Internal server error' })
}
```

---

## Route Setup

```typescript
// src/routes/productRoutes.ts
import { Router } from 'express'
import { productController } from '../controllers'
import { ValidateUID, ValidateUserAID } from '../middleware/auth'

const router = Router()

router.post('/', ValidateUID, productController.create)
router.get('/', ValidateUID, productController.findAll)
router.get('/:id', ValidateUID, ValidateUserAID('Product'), productController.findById)
router.put('/:id', ValidateUID, ValidateUserAID('Product'), productController.update)
router.delete('/:id', ValidateUID, ValidateUserAID('Product'), productController.delete)

export default router
```
