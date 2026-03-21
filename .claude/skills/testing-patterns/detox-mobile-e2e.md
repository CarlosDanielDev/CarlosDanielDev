# Detox E2E Testing for mobile-app

Complete guide for mobile end-to-end testing with Detox.

---

## Detox Configuration

```javascript
// e2e/config/detox.config.js
module.exports = {
  testRunner: 'jest',
  runnerConfig: 'e2e/config/jest.config.js',
  configurations: {
    'ios.sim.debug': {
      device: { type: 'iPhone 14' },
      app: { build: 'ios.debug', type: 'ios.app' },
    },
    'android.emu.debug': {
      device: { avdName: 'Pixel_4_API_30' },
      app: { build: 'android.debug', type: 'android.apk' },
    },
  },
}
```

---

## Authentication Test

```javascript
// e2e/auth/login.e2e.js
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp()
  })

  beforeEach(async () => {
    await device.reloadReactNative()
  })

  it('should login successfully with valid credentials', async () => {
    // Navigate to login
    await expect(element(by.id('login-screen'))).toBeVisible()

    // Fill credentials
    await element(by.id('email-input')).typeText('user@example.com')
    await element(by.id('password-input')).typeText('password123')

    // Submit
    await element(by.id('login-button')).tap()

    // Verify navigation to dashboard
    await waitFor(element(by.id('dashboard-screen')))
      .toBeVisible()
      .withTimeout(5000)

    await expect(element(by.id('welcome-message'))).toBeVisible()
  })

  it('should show error for invalid credentials', async () => {
    await element(by.id('email-input')).typeText('wrong@example.com')
    await element(by.id('password-input')).typeText('wrongpassword')
    await element(by.id('login-button')).tap()

    await expect(element(by.id('error-message'))).toBeVisible()
    await expect(element(by.id('error-message'))).toHaveText('Invalid credentials')
  })

  it('should require both email and password', async () => {
    await element(by.id('login-button')).tap()

    await expect(element(by.id('email-error'))).toBeVisible()
    await expect(element(by.id('password-error'))).toBeVisible()
  })
})
```

---

## CRUD Operations Test

```javascript
// e2e/products/product-crud.e2e.js
describe('Product CRUD', () => {
  beforeAll(async () => {
    await device.launchApp()
    await loginAsTestUser()
  })

  it('should create a new product', async () => {
    // Navigate to products
    await element(by.id('tab-products')).tap()
    await expect(element(by.id('products-list'))).toBeVisible()

    // Create new product
    await element(by.id('add-product-button')).tap()
    await expect(element(by.id('product-form'))).toBeVisible()

    // Fill form
    await element(by.id('product-name-input')).typeText('Test Product')
    await element(by.id('product-price-input')).typeText('29.99')
    await element(by.id('product-description-input')).typeText('A test product')

    // Save
    await element(by.id('save-product-button')).tap()

    // Verify product appears in list
    await waitFor(element(by.text('Test Product')))
      .toBeVisible()
      .withTimeout(5000)
  })

  it('should edit an existing product', async () => {
    // Find and tap product
    await element(by.text('Test Product')).tap()
    await expect(element(by.id('product-detail-screen'))).toBeVisible()

    // Edit
    await element(by.id('edit-product-button')).tap()
    await element(by.id('product-name-input')).clearText()
    await element(by.id('product-name-input')).typeText('Updated Product')
    await element(by.id('save-product-button')).tap()

    // Verify update
    await expect(element(by.text('Updated Product'))).toBeVisible()
  })

  it('should delete a product', async () => {
    await element(by.text('Updated Product')).tap()
    await element(by.id('delete-product-button')).tap()

    // Confirm deletion
    await element(by.id('confirm-delete-button')).tap()

    // Verify product removed
    await waitFor(element(by.text('Updated Product')))
      .not.toBeVisible()
      .withTimeout(3000)
  })
})
```

---

## Navigation Testing

```javascript
// e2e/navigation/navigation.e2e.js
describe('Navigation', () => {
  beforeAll(async () => {
    await device.launchApp()
    await loginAsTestUser()
  })

  it('should navigate through all main tabs', async () => {
    const tabs = ['home', 'products', 'sales', 'customers', 'settings']

    for (const tab of tabs) {
      await element(by.id(`tab-${tab}`)).tap()
      await expect(element(by.id(`${tab}-screen`))).toBeVisible()
    }
  })

  it('should handle back navigation correctly', async () => {
    await element(by.id('tab-products')).tap()
    await element(by.id('add-product-button')).tap()
    await expect(element(by.id('product-form'))).toBeVisible()

    // Go back
    await element(by.id('back-button')).tap()
    await expect(element(by.id('products-list'))).toBeVisible()
  })

  it('should handle deep linking', async () => {
    await device.openURL({
      url: 'myapp://products/123',
    })

    await expect(element(by.id('product-detail-screen'))).toBeVisible()
  })
})
```

---

## List Scrolling Test

```javascript
// e2e/lists/scrolling.e2e.js
describe('List Scrolling', () => {
  beforeAll(async () => {
    await device.launchApp()
    await loginAsTestUser()
  })

  it('should scroll to bottom of products list', async () => {
    await element(by.id('tab-products')).tap()

    // Scroll to bottom
    await element(by.id('products-list')).scrollTo('bottom')

    // Verify last item visible
    await expect(element(by.id('product-item-49'))).toBeVisible()
  })

  it('should scroll to specific item', async () => {
    await element(by.id('products-list')).scroll(500, 'down')
    await expect(element(by.text('Product 20'))).toBeVisible()
  })
})
```

---

## Form Validation Test

```javascript
// e2e/forms/validation.e2e.js
describe('Form Validation', () => {
  beforeAll(async () => {
    await device.launchApp()
    await loginAsTestUser()
    await element(by.id('tab-products')).tap()
    await element(by.id('add-product-button')).tap()
  })

  it('should show error for empty name', async () => {
    await element(by.id('save-product-button')).tap()
    await expect(element(by.id('name-error'))).toBeVisible()
    await expect(element(by.id('name-error'))).toHaveText('Name is required')
  })

  it('should show error for invalid price', async () => {
    await element(by.id('product-price-input')).typeText('invalid')
    await element(by.id('save-product-button')).tap()
    await expect(element(by.id('price-error'))).toBeVisible()
  })

  it('should clear errors when fixed', async () => {
    await element(by.id('product-name-input')).typeText('Valid Name')
    await expect(element(by.id('name-error'))).not.toBeVisible()
  })
})
```

---

## Helper Functions

```javascript
// e2e/utils/helpers.js

export const loginAsTestUser = async () => {
  await element(by.id('email-input')).typeText('test@example.com')
  await element(by.id('password-input')).typeText('password123')
  await element(by.id('login-button')).tap()
  await waitFor(element(by.id('dashboard-screen')))
    .toBeVisible()
    .withTimeout(5000)
}

export const logout = async () => {
  await element(by.id('tab-settings')).tap()
  await element(by.id('logout-button')).tap()
  await element(by.id('confirm-logout')).tap()
  await waitFor(element(by.id('login-screen')))
    .toBeVisible()
    .withTimeout(3000)
}

export const createTestProduct = async (name = 'Test Product') => {
  await element(by.id('tab-products')).tap()
  await element(by.id('add-product-button')).tap()
  await element(by.id('product-name-input')).typeText(name)
  await element(by.id('product-price-input')).typeText('29.99')
  await element(by.id('save-product-button')).tap()
  await waitFor(element(by.text(name))).toBeVisible().withTimeout(5000)
}
```

---

## Platform-Specific Tests

### iOS-Specific

```javascript
// e2e/platform/ios-specific.e2e.js
describe('iOS Specific', () => {
  it('should handle swipe to delete', async () => {
    await element(by.id('product-item-0')).swipe('left')
    await expect(element(by.id('delete-action'))).toBeVisible()
  })

  it('should handle pull to refresh', async () => {
    await element(by.id('products-list')).swipe('down', 'slow', 0.5)
    await waitFor(element(by.id('refresh-indicator')))
      .not.toBeVisible()
      .withTimeout(3000)
  })
})
```

### Android-Specific

```javascript
// e2e/platform/android-specific.e2e.js
describe('Android Specific', () => {
  it('should handle Android back button', async () => {
    await element(by.id('tab-products')).tap()
    await element(by.id('add-product-button')).tap()

    // Use Android back button
    await device.pressBack()

    await expect(element(by.id('products-list'))).toBeVisible()
  })

  it('should dismiss keyboard with back button', async () => {
    await element(by.id('search-input')).tap()
    await device.pressBack()
    // Keyboard should be dismissed
  })
})
```

---

## Detox Matchers Reference

```javascript
// Visibility
await expect(element(by.id('my-id'))).toBeVisible()
await expect(element(by.id('my-id'))).not.toBeVisible()

// Text
await expect(element(by.id('my-text'))).toHaveText('Hello')
await expect(element(by.id('my-text'))).not.toHaveText('Goodbye')

// Value
await expect(element(by.id('my-input'))).toHaveValue('Value')

// Existence
await expect(element(by.id('my-id'))).toExist()
await expect(element(by.id('my-id'))).not.toExist()
```

---

## Detox Actions Reference

```javascript
// Tap
await element(by.id('button')).tap()
await element(by.id('button')).multiTap(3)
await element(by.id('button')).longPress()

// Type
await element(by.id('input')).typeText('Hello')
await element(by.id('input')).replaceText('New text')
await element(by.id('input')).clearText()

// Scroll
await element(by.id('scrollView')).scrollTo('bottom')
await element(by.id('scrollView')).scrollTo('top')
await element(by.id('scrollView')).scroll(100, 'down')

// Swipe
await element(by.id('card')).swipe('up')
await element(by.id('card')).swipe('left', 'fast')
```

---

## Commands Reference

```bash
# Build for testing
yarn detox build -c ios.sim.debug
yarn detox build -c android.emu.debug

# Run E2E tests
yarn detox test -c ios.sim.debug
yarn detox test -c android.emu.debug

# Run specific test file
yarn detox test -c ios.sim.debug e2e/auth/login.e2e.js

# Run with reuse (faster)
yarn detox test -c ios.sim.debug --reuse

# Clean and rebuild
yarn detox clean-framework-cache
yarn detox build -c ios.sim.debug
```
