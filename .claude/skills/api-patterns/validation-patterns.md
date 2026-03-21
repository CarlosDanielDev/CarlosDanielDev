# Zod Validation Patterns for api

Input/output validation with Zod.

---

## Basic Schema

```typescript
// src/validation/schemas/productSchemas.ts
import { z } from 'zod'

export const CreateProductSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  price: z.number().positive('Price must be positive'),
  description: z.string().optional(),
  category: z.enum(['electronics', 'clothing', 'food']),
  tags: z.array(z.string()).optional(),
})

export type CreateProductInput = z.infer<typeof CreateProductSchema>

export const UpdateProductSchema = CreateProductSchema.partial()
```

---

## Using in Controllers

```typescript
export const createProduct = async (req: Request, res: Response) => {
  try {
    // Validate and parse
    const data = CreateProductSchema.parse(req.body)

    // data is now typed as CreateProductInput
    const product = await productService.create(data, req.user.aid)

    res.status(201).json(product)
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({
        error: 'Validation failed',
        details: error.errors
      })
    }
    res.status(500).json({ error: 'Internal server error' })
  }
}
```

---

## Custom Validators

```typescript
const EmailSchema = z.string().email().refine(
  async (email) => {
    const exists = await User.findOne({ email })
    return !exists
  },
  { message: 'Email already registered' }
)

const PasswordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[a-z]/, 'Must contain lowercase')
  .regex(/[A-Z]/, 'Must contain uppercase')
  .regex(/[0-9]/, 'Must contain number')
```

---

## Validation Middleware

```typescript
// src/middleware/validate.ts
export const validate = (schema: z.ZodSchema) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      req.body = schema.parse(req.body)
      next()
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({
          error: 'Validation failed',
          details: error.errors
        })
      }
      next(error)
    }
  }
}

// Usage
router.post('/products', validate(CreateProductSchema), createProduct)
```
