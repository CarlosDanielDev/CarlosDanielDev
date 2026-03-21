---
name: testing-patterns
version: "1.0.0"
description: Testing patterns for mobile-app (Detox E2E, mobile), web-app (Playwright, Storybook), and api (Supertest, Jest). Use when designing tests, creating test specifications, or analyzing test coverage.
allowed-tools: Read, Grep, Glob, WebSearch
---

# Testing Patterns

Quick reference for testing patterns across all platforms.

## Skill Usage

| Aspect | Details |
|--------|---------|
| **Consumers** | `subagent-qa-mobile`, `subagent-qa-backend`, `subagent-qa-frontend` |
| **Purpose** | Test patterns, examples, and specifications |
| **Invocation** | QA subagents read this skill; NOT directly invocable by users |
| **Related Skills** | `mobile-patterns`, `shared-patterns` |

---

## Testing Stack by Platform

### 📱 Mobile (mobile-app)

| Type | Tool | Commands |
|------|------|----------|
| Unit Tests | Jest | `yarn test` |
| E2E Tests | Detox | `yarn detox build` + `yarn detox test` |
| Lint | ESLint | `yarn lint` |
| Device Matrix | Manual | Small phone, Large phone, Tablet |

### 🌐 Frontend Web (web-app)

| Type | Tool | Commands |
|------|------|----------|
| Unit Tests | Jest + Testing Library | `yarn test` |
| E2E Tests | Playwright | `yarn test:e2e` |
| Visual Regression | Playwright + Percy | `yarn test:visual` |
| Component Tests | Storybook | `yarn storybook` |
| Accessibility | axe-core | Integrated in Playwright |

### 🔧 Backend (api)

| Type | Tool | Commands |
|------|------|----------|
| Unit Tests | Jest | `yarn test` |
| Integration Tests | Supertest + MongoDB Memory Server | `yarn test:integration` |
| API Tests | Supertest | Included in integration |
| Coverage | Jest | `yarn test:coverage` |

---

## Quick Test Patterns

### Mobile E2E (Detox)

```javascript
describe('Products', () => {
  beforeAll(async () => {
    await device.launchApp()
  })

  it('should display products list', async () => {
    await expect(element(by.id('products-list'))).toBeVisible()
    await expect(element(by.id('product-item-0'))).toBeVisible()
  })
})
```

### Frontend E2E (Playwright)

```typescript
test('should login successfully', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[data-testid="email-input"]', 'user@example.com')
  await page.fill('[data-testid="password-input"]', 'password')
  await page.click('[data-testid="login-button"]')

  await expect(page.locator('[data-testid="dashboard"]')).toBeVisible()
})
```

### Backend API Test (Supertest)

```typescript
describe('POST /api/products', () => {
  it('should create a product', async () => {
    const response = await request(app)
      .post('/api/products')
      .send({ name: 'Test Product', price: 29.99 })
      .expect(201)

    expect(response.body.name).toBe('Test Product')
  })
})
```

---

## Critical Testing Pattern: testID

### Mobile (generateTestID)

```typescript
import { generateTestID } from '../../util'

<Button {...generateTestID('save-button')} onPress={handleSave}>
  Save
</Button>
```

### Web (data-testid)

```typescript
<button data-testid="save-button" onClick={handleSave}>
  Save
</button>
```

---

## Detailed Testing Guides

For comprehensive test patterns, see:

- **[detox-mobile-e2e.md](detox-mobile-e2e.md)** - Mobile E2E testing
  - Detox setup and configuration
  - Authentication flows
  - CRUD operations
  - Navigation testing
  - Platform-specific tests

- **[mobile-device-matrix.md](mobile-device-matrix.md)** - Device testing
  - Small phone, Large phone, Tablet specs
  - Layout testing strategies
  - Touch target validation
  - Device-specific configuration

- **[mobile-performance.md](mobile-performance.md)** - Performance testing
  - Startup time measurement
  - Screen load metrics
  - Memory profiling
  - Performance thresholds

- **[playwright-web-e2e.md](playwright-web-e2e.md)** - Web E2E testing
  - Playwright setup
  - Page Object Model
  - Authentication flows
  - Form testing
  - API mocking

- **[playwright-visual.md](playwright-visual.md)** - Visual regression
  - Screenshot testing
  - Figma design comparison
  - Visual diff strategies
  - Baseline management

- **[storybook-testing.md](storybook-testing.md)** - Component testing
  - Storybook configuration
  - Story templates
  - Snapshot testing
  - Interaction testing

- **[supertest-api.md](supertest-api.md)** - Backend API testing
  - Supertest setup
  - Request/response testing
  - Authentication testing
  - Error handling tests

- **[jest-integration.md](jest-integration.md)** - Integration testing
  - MongoDB Memory Server setup
  - Service layer testing
  - Repository pattern testing
  - Test data factories

- **[accessibility-testing.md](accessibility-testing.md)** - a11y testing
  - axe-core integration
  - WCAG compliance
  - Screen reader testing
  - Keyboard navigation

---

## Test Structure Best Practices

### Naming Convention

```
Feature.Action.ExpectedResult

Examples:
- Login.WithValidCredentials.ShouldSucceed
- ProductList.WhenEmpty.ShouldShowEmptyState
- API.CreateProduct.ShouldReturn201
```

### AAA Pattern (Arrange-Act-Assert)

```typescript
it('should add product to cart', async () => {
  // Arrange
  const product = { id: '123', name: 'Test Product' }

  // Act
  await addToCart(product)

  // Assert
  expect(cart.items).toContain(product)
})
```

---

## Quality Gates

### Mobile (mobile-app)

| Metric | Threshold | Status |
|--------|-----------|--------|
| E2E pass rate | 100% | PASS/FAIL |
| Startup time | < 3s | PASS/CONCERNS/FAIL |
| Screen load | < 2s | PASS/CONCERNS/FAIL |
| testID coverage | 100% interactive | PASS/FAIL |

### Frontend (web-app)

| Metric | Threshold | Status |
|--------|-----------|--------|
| E2E pass rate | 100% | PASS/FAIL |
| Visual similarity | > 95% | PASS/FAIL |
| Accessibility score | 100 | PASS/CONCERNS/FAIL |
| Unit test coverage | > 80% | PASS/CONCERNS |

### Backend (api)

| Metric | Threshold | Status |
|--------|-----------|--------|
| Unit tests | 100% pass | PASS/FAIL |
| Integration tests | 100% pass | PASS/FAIL |
| Code coverage | > 80% | PASS/CONCERNS |
| API response time | < 200ms | PASS/CONCERNS |

---

## When to Consult This Skill

- Writing test specifications for QA subagents
- Analyzing test coverage gaps
- Designing E2E test scenarios
- Creating device matrix test plans
- Setting up testing infrastructure
- Reviewing test quality and completeness
