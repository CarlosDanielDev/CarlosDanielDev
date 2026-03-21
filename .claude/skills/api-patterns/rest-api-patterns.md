# REST API Patterns for api

RESTful API design conventions.

---

## Endpoint Naming

```
# Resources (plural nouns)
GET    /api/products
GET    /api/products/:id
POST   /api/products
PUT    /api/products/:id
DELETE /api/products/:id

# Nested resources
GET    /api/products/:id/variants
POST   /api/products/:id/variants

# Actions (verbs)
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/orders/:id/cancel
```

---

## HTTP Methods & Status Codes

| Method | Purpose | Success Status |
|--------|---------|----------------|
| GET | Retrieve resource(s) | 200 OK |
| POST | Create resource | 201 Created |
| PUT | Update resource | 200 OK |
| PATCH | Partial update | 200 OK |
| DELETE | Delete resource | 204 No Content |

### Error Status Codes

- `400` - Bad Request (validation failed)
- `401` - Unauthorized (not authenticated)
- `403` - Forbidden (not authorized)
- `404` - Not Found
- `409` - Conflict (duplicate)
- `500` - Internal Server Error

---

## Request/Response Format

### Request

```typescript
POST /api/products
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "Product Name",
  "price": 29.99,
  "description": "Description"
}
```

### Response

```typescript
// Success
HTTP/1.1 201 Created
Content-Type: application/json

{
  "_id": "507f1f77bcf86cd799439011",
  "name": "Product Name",
  "price": 29.99,
  "createdAt": "2024-01-01T00:00:00Z"
}

// Error
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Validation failed",
  "details": [
    { "field": "name", "message": "Name is required" }
  ]
}
```

---

## Pagination

```typescript
GET /api/products?page=1&limit=20

Response:
{
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

---

## Filtering & Sorting

```typescript
// Filtering
GET /api/products?status=active&category=electronics

// Sorting
GET /api/products?sort=-createdAt,name  // - for descending

// Combined
GET /api/products?status=active&sort=-price&page=1&limit=10
```
