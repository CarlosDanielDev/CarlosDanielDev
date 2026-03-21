# Authentication Patterns for api

Authentication and authorization middleware.

---

## ValidateUID Middleware

Validates JWT token and extracts user.

```typescript
// src/middleware/auth/ValidateUID.ts
import jwt from 'jsonwebtoken'

export const ValidateUID = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '')

    if (!token) {
      return res.status(401).json({ error: 'No token provided' })
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET!)
    req.user = decoded

    next()
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' })
  }
}
```

---

## ValidateUserAID Middleware

Validates resource ownership.

```typescript
// src/middleware/auth/ValidateUserAID.ts
export const ValidateUserAID = (Model: string) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const resourceId = req.params.id
      const userAid = req.user.aid

      // Find resource
      const model = mongoose.model(Model)
      const resource = await model.findById(resourceId)

      if (!resource) {
        return res.status(404).json({ error: `${Model} not found` })
      }

      // Check ownership
      if (resource.aid !== userAid) {
        return res.status(403).json({ error: 'Access denied' })
      }

      next()
    } catch (error) {
      res.status(500).json({ error: 'Internal server error' })
    }
  }
}

// Usage
router.put('/products/:id',
  ValidateUID,
  ValidateUserAID('Product'),
  updateProduct
)
```

---

## Role-Based Access Control

```typescript
export const requireRole = (roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Unauthorized' })
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Forbidden' })
    }

    next()
  }
}

// Usage
router.delete('/users/:id', requireRole(['admin']), deleteUser)
```
