# OWASP Top 10 (2021)

Complete guide to OWASP Top 10 vulnerabilities.

---

## A01:2021 - Broken Access Control

### What to Look For
- Missing authorization checks on endpoints/functions
- IDOR (Insecure Direct Object References)
- Path traversal vulnerabilities
- CORS misconfigurations
- Missing function-level access control

### Detection
```typescript
// ❌ VULNERABLE - No ownership check
app.get('/api/orders/:id', async (req, res) => {
  const order = await Order.findById(req.params.id)
  res.json(order) // Any user can see any order!
})

// ✅ SECURE - Ownership validation
app.get('/api/orders/:id', async (req, res) => {
  const order = await Order.findById(req.params.id)
  if (!order) return res.status(404).send()
  if (order.userId !== req.user.id) return res.status(403).send()
  res.json(order)
})
```

---

## A02:2021 - Cryptographic Failures

### What to Look For
- Hardcoded secrets, API keys, passwords
- Weak encryption algorithms (MD5, SHA1 for passwords)
- Cleartext sensitive data storage
- Improper key management
- Sensitive data in logs

### Detection
```typescript
// ❌ VULNERABLE
const API_KEY = 'sk-abc123' // Hardcoded
const hash = md5(password) // Weak algorithm
localStorage.setItem('token', token) // Cleartext storage

// ✅ SECURE
const API_KEY = process.env.API_KEY
const hash = await bcrypt.hash(password, 10)
// Use httpOnly cookies for tokens
```

---

## A03:2021 - Injection

### SQL Injection
```typescript
// ❌ VULNERABLE
const query = `SELECT * FROM users WHERE email = '${req.body.email}'`

// ✅ SECURE - Parameterized query
const query = 'SELECT * FROM users WHERE email = ?'
db.query(query, [req.body.email])
```

### NoSQL Injection
```typescript
// ❌ VULNERABLE
db.find({ username: req.body.username })

// ✅ SECURE
db.find({ username: { $eq: req.body.username } })
```

### Command Injection
```typescript
// ❌ VULNERABLE
exec(`convert ${req.body.filename}.png output.jpg`)

// ✅ SECURE
if (!/^[a-zA-Z0-9_-]+$/.test(filename)) throw new Error('Invalid filename')
execFile('convert', [`${filename}.png`, 'output.jpg'])
```

---

## A04:2021 - Insecure Design

### What to Look For
- Missing rate limiting
- Lack of input validation architecture
- Missing account lockout mechanisms
- Insufficient logging for security events

### Detection
```typescript
// ❌ INSECURE DESIGN - No rate limiting
app.post('/api/login', handleLogin)

// ✅ SECURE DESIGN
import rateLimit from 'express-rate-limit'

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  message: 'Too many login attempts'
})

app.post('/api/login', loginLimiter, handleLogin)
```

---

## A05:2021 - Security Misconfiguration

### What to Look For
- Debug mode in production
- Default credentials
- Verbose error messages
- Missing security headers
- Outdated dependencies

### Detection
```typescript
// ❌ MISCONFIGURED
if (err) {
  res.status(500).json({ error: err.stack }) // Verbose error
}

// ✅ SECURE
if (err) {
  console.error(err) // Log internally
  res.status(500).json({ error: 'Internal server error' }) // Generic message
}

// Security headers
import helmet from 'helmet'
app.use(helmet())
```

---

## A06:2021 - Vulnerable Components

### What to Look For
- Outdated dependencies with known CVEs
- Abandoned packages
- Typosquatting risks

### Detection
```bash
# Check for vulnerabilities
npm audit
npm outdated
npx snyk test
```

---

## A07:2021 - Authentication Failures

### What to Look For
- Weak password policies
- Missing brute force protection
- Session fixation vulnerabilities
- Insecure session management

### Detection
```typescript
// ❌ VULNERABLE
const password = req.body.password // No validation

// ✅ SECURE
const passwordSchema = z.string()
  .min(8)
  .regex(/[a-z]/, 'Must contain lowercase')
  .regex(/[A-Z]/, 'Must contain uppercase')
  .regex(/[0-9]/, 'Must contain number')
  .regex(/[^a-zA-Z0-9]/, 'Must contain special char')
```

---

## A08:2021 - Software and Data Integrity Failures

### What to Look For
- Insecure deserialization
- Missing integrity checks on updates
- Unsafe use of eval/Function constructor
- CI/CD pipeline vulnerabilities

### Detection
```typescript
// ❌ VULNERABLE
eval(userInput) // Never use eval with user input
const fn = new Function(userInput)()

// ✅ SECURE
// Use safe alternatives like JSON.parse with validation
const data = JSON.parse(userInput)
if (!schema.safeParse(data).success) throw new Error('Invalid data')
```

---

## A09:2021 - Security Logging and Monitoring Failures

### What to Look For
- Missing audit logs for security events
- Sensitive data in logs
- Insufficient log detail
- Missing alerting mechanisms

### Detection
```typescript
// ❌ INSUFFICIENT
app.post('/api/login', async (req, res) => {
  // No logging
})

// ✅ SECURE
app.post('/api/login', async (req, res) => {
  try {
    const user = await authenticateUser(req.body)
    logger.info('Login successful', {
      userId: user.id,
      ip: req.ip,
      timestamp: new Date()
    })
  } catch (err) {
    logger.warn('Login failed', {
      email: req.body.email,
      ip: req.ip,
      reason: 'Invalid credentials'
    })
  }
})
```

---

## A10:2021 - Server-Side Request Forgery (SSRF)

### What to Look For
- User-controlled URLs in server requests
- Missing URL validation
- Internal service access from user input

### Detection
```typescript
// ❌ VULNERABLE
const response = await fetch(req.body.url)

// ✅ SECURE
const allowedDomains = ['api.example.com', 'cdn.example.com']
const url = new URL(req.body.url)

if (!allowedDomains.includes(url.hostname)) {
  throw new Error('Domain not allowed')
}

const response = await fetch(url.toString())
```
