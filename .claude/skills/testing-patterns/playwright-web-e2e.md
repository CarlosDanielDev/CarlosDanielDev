# Playwright E2E Testing for web-app

End-to-end testing patterns for React Web with Playwright.

---

## Playwright Configuration

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
})
```

---

## Authentication Test

```typescript
// e2e/auth/login.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Login', () => {
  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[data-testid="email-input"]', 'user@example.com')
    await page.fill('[data-testid="password-input"]', 'password123')
    await page.click('[data-testid="login-button"]')

    await expect(page.locator('[data-testid="dashboard"]')).toBeVisible()
  })

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[data-testid="email-input"]', 'wrong@example.com')
    await page.fill('[data-testid="password-input"]', 'wrongpass')
    await page.click('[data-testid="login-button"]')

    await expect(page.locator('[data-testid="error-message"]')).toBeVisible()
    await expect(page.locator('[data-testid="error-message"]')).toHaveText('Invalid credentials')
  })
})
```

---

## CRUD Operations Test

```typescript
// e2e/products/crud.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Product CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('[data-testid="email-input"]', 'test@example.com')
    await page.fill('[data-testid="password-input"]', 'password')
    await page.click('[data-testid="login-button"]')
    await page.waitForURL('/dashboard')
  })

  test('should create product', async ({ page }) => {
    await page.goto('/products')
    await page.click('[data-testid="add-product-button"]')

    await page.fill('[data-testid="name-input"]', 'Test Product')
    await page.fill('[data-testid="price-input"]', '29.99')
    await page.click('[data-testid="save-button"]')

    await expect(page.locator('text=Test Product')).toBeVisible()
  })

  test('should edit product', async ({ page }) => {
    await page.goto('/products')
    await page.click('[data-testid="product-item-0"]')
    await page.click('[data-testid="edit-button"]')

    await page.fill('[data-testid="name-input"]', 'Updated Product')
    await page.click('[data-testid="save-button"]')

    await expect(page.locator('text=Updated Product')).toBeVisible()
  })

  test('should delete product', async ({ page }) => {
    await page.goto('/products')
    await page.click('[data-testid="product-item-0"]')
    await page.click('[data-testid="delete-button"]')
    await page.click('[data-testid="confirm-delete"]')

    await expect(page.locator('[data-testid="product-item-0"]')).not.toBeVisible()
  })
})
```

---

## Form Testing

```typescript
// e2e/forms/validation.spec.ts
test('should validate required fields', async ({ page }) => {
  await page.goto('/products/new')
  await page.click('[data-testid="save-button"]')

  await expect(page.locator('[data-testid="name-error"]')).toBeVisible()
  await expect(page.locator('[data-testid="name-error"]')).toHaveText('Name is required')
})

test('should clear errors when field is filled', async ({ page }) => {
  await page.goto('/products/new')
  await page.click('[data-testid="save-button"]')
  await expect(page.locator('[data-testid="name-error"]')).toBeVisible()

  await page.fill('[data-testid="name-input"]', 'Valid Name')
  await expect(page.locator('[data-testid="name-error"]')).not.toBeVisible()
})
```

---

## Page Object Model

```typescript
// e2e/pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login')
  }

  async login(email: string, password: string) {
    await this.page.fill('[data-testid="email-input"]', email)
    await this.page.fill('[data-testid="password-input"]', password)
    await this.page.click('[data-testid="login-button"]')
  }

  async expectError(message: string) {
    await expect(this.page.locator('[data-testid="error-message"]')).toHaveText(message)
  }
}

// Usage
test('login test', async ({ page }) => {
  const loginPage = new LoginPage(page)
  await loginPage.goto()
  await loginPage.login('user@example.com', 'password')
})
```

---

## API Mocking

```typescript
test('should handle API errors', async ({ page }) => {
  // Mock API failure
  await page.route('**/api/products', route => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Server error' }),
    })
  })

  await page.goto('/products')
  await expect(page.locator('[data-testid="error-message"]')).toBeVisible()
})

test('should load products from mocked API', async ({ page }) => {
  await page.route('**/api/products', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify([
        { id: '1', name: 'Product 1' },
        { id: '2', name: 'Product 2' },
      ]),
    })
  })

  await page.goto('/products')
  await expect(page.locator('text=Product 1')).toBeVisible()
})
```

---

## Commands Reference

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test e2e/auth/login.spec.ts

# Run in headed mode
npx playwright test --headed

# Run in specific browser
npx playwright test --project=chromium

# Debug test
npx playwright test --debug

# Generate test report
npx playwright show-report
```
