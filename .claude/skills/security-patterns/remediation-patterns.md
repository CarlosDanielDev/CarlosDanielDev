# Security Remediation Patterns

How to fix common security vulnerabilities.

---

## Injection Fixes

### SQL Injection

```typescript
// BEFORE (vulnerable)
const query = `SELECT * FROM users WHERE email = '${email}'`
db.query(query)

// AFTER (secure)
const query = 'SELECT * FROM users WHERE email = ?'
db.query(query, [email])
```

### NoSQL Injection

```typescript
// BEFORE (vulnerable)
User.findOne({ username: req.body.username })

// AFTER (secure)
User.findOne({ username: { $eq: req.body.username } })

// Or use Zod validation
const schema = z.object({
  username: z.string().regex(/^[a-zA-Z0-9_-]+$/)
})
const { username } = schema.parse(req.body)
User.findOne({ username })
```

### Command Injection

```typescript
// BEFORE (vulnerable)
exec(`ffmpeg -i ${inputFile} output.mp4`)

// AFTER (secure)
import { execFile } from 'child_process'
import { promisify } from 'util'

const execFileAsync = promisify(execFile)

// Validate input
if (!/^[a-zA-Z0-9_-]+\.(mp4|avi)$/.test(inputFile)) {
  throw new Error('Invalid file name')
}

await execFileAsync('ffmpeg', ['-i', inputFile, 'output.mp4'])
```

---

## Authentication Fixes

### Password Hashing

```typescript
// BEFORE (vulnerable)
user.password = req.body.password

// AFTER (secure)
import bcrypt from 'bcrypt'

const SALT_ROUNDS = 10
user.passwordHash = await bcrypt.hash(req.body.password, SALT_ROUNDS)

// Login verification
const isValid = await bcrypt.compare(req.body.password, user.passwordHash)
```

### Password Policy

```typescript
import { z } from 'zod'

const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[a-z]/, 'Must contain lowercase letter')
  .regex(/[A-Z]/, 'Must contain uppercase letter')
  .regex(/[0-9]/, 'Must contain number')
  .regex(/[^a-zA-Z0-9]/, 'Must contain special character')

// Usage
const { password } = passwordSchema.parse(req.body)
```

### Rate Limiting

```typescript
import rateLimit from 'express-rate-limit'

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  skipSuccessfulRequests: true,
  message: 'Too many login attempts, please try again later'
})

app.post('/api/login', loginLimiter, handleLogin)
```

---

## Authorization Fixes

### Resource Ownership Check

```typescript
// BEFORE (vulnerable)
app.get('/api/orders/:id', async (req, res) => {
  const order = await Order.findById(req.params.id)
  res.json(order)
})

// AFTER (secure)
app.get('/api/orders/:id', authenticateUser, async (req, res) => {
  const order = await Order.findById(req.params.id)

  if (!order) {
    return res.status(404).json({ error: 'Order not found' })
  }

  // Check ownership
  if (order.userId.toString() !== req.user.id) {
    return res.status(403).json({ error: 'Forbidden' })
  }

  res.json(order)
})
```

### Role-Based Access Control

```typescript
const requireRole = (roles: string[]) => {
  return (req, res, next) => {
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
app.delete('/api/users/:id', requireRole(['admin']), deleteUser)
```

---

## XSS Fixes

### React

```typescript
// BEFORE (vulnerable)
<div dangerouslySetInnerHTML={{__html: userInput}} />

// AFTER (secure)
<div>{userInput}</div> // React escapes by default

// If HTML is needed, sanitize first
import DOMPurify from 'dompurify'
<div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userInput)}} />
```

### Server-Side Rendering

```typescript
import escapeHtml from 'escape-html'

// BEFORE (vulnerable)
const html = `<div>${userInput}</div>`

// AFTER (secure)
const html = `<div>${escapeHtml(userInput)}</div>`
```

---

## Cryptographic Fixes

### Remove Hardcoded Secrets

```typescript
// BEFORE (vulnerable)
const API_KEY = 'sk-abc123def456'
const DB_PASSWORD = 'admin123'

// AFTER (secure)
const API_KEY = process.env.API_KEY
const DB_PASSWORD = process.env.DB_PASSWORD

// Validate env vars
if (!API_KEY || !DB_PASSWORD) {
  throw new Error('Missing required environment variables')
}
```

### Secure Token Storage

```typescript
// BEFORE (vulnerable - localStorage)
localStorage.setItem('authToken', token)

// AFTER (secure - httpOnly cookie)
res.cookie('authToken', token, {
  httpOnly: true,
  secure: true, // HTTPS only
  sameSite: 'strict',
  maxAge: 24 * 60 * 60 * 1000 // 24 hours
})
```

---

## Error Handling Fixes

```typescript
// BEFORE (vulnerable - verbose errors)
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack // Exposes internals!
  })
})

// AFTER (secure - generic errors)
app.use((err, req, res, next) => {
  // Log full error internally
  logger.error('Error occurred', {
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method
  })

  // Send generic error to client
  res.status(500).json({
    error: 'Internal server error'
  })
})
```
