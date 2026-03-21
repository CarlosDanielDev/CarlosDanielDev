# HTTP Security Headers

Essential security headers for web applications.

---

## Helmet.js (Express)

```typescript
import helmet from 'helmet'

app.use(helmet())
```

This sets multiple security headers automatically.

---

## Content-Security-Policy (CSP)

Prevents XSS by controlling which resources can be loaded.

```typescript
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'"], // Avoid unsafe-inline in production
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "https:"],
    connectSrc: ["'self'", "https://api.example.com"],
    fontSrc: ["'self'"],
    objectSrc: ["'none'"],
    mediaSrc: ["'self'"],
    frameSrc: ["'none'"],
  },
}))
```

---

## X-Frame-Options

Prevents clickjacking attacks.

```typescript
app.use(helmet.frameguard({ action: 'deny' }))
```

Values:
- `DENY` - No framing allowed
- `SAMEORIGIN` - Only same origin can frame
- `ALLOW-FROM uri` - Specific URI can frame (deprecated)

---

## Strict-Transport-Security (HSTS)

Forces HTTPS connections.

```typescript
app.use(helmet.hsts({
  maxAge: 31536000, // 1 year in seconds
  includeSubDomains: true,
  preload: true
}))
```

---

## X-Content-Type-Options

Prevents MIME sniffing.

```typescript
app.use(helmet.noSniff())
```

Sets: `X-Content-Type-Options: nosniff`

---

## X-XSS-Protection

Legacy XSS protection (for older browsers).

```typescript
app.use(helmet.xssFilter())
```

Sets: `X-XSS-Protection: 1; mode=block`

---

## Referrer-Policy

Controls referrer information.

```typescript
app.use(helmet.referrerPolicy({ policy: 'no-referrer' }))
```

---

## Permissions-Policy

Controls browser features.

```typescript
app.use((req, res, next) => {
  res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
  next()
})
```

---

## Complete Security Headers Setup

```typescript
import express from 'express'
import helmet from 'helmet'

const app = express()

// Apply all security headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  },
}))

// Additional custom headers
app.use((req, res, next) => {
  res.setHeader('X-Permitted-Cross-Domain-Policies', 'none')
  res.setHeader('X-Download-Options', 'noopen')
  next()
})
```
