# Mobile Device Matrix Testing

Device coverage requirements for mobile-app.

---

## Device Matrix Specifications

### Small Phone (width <= 375)
- **iOS**: iPhone SE (375 x 667)
- **Android**: Pixel 4a (393 x 851)
- **Tests**: Layout, text truncation, touch targets (44x44 minimum)

### Large Phone (width > 375, <= 430)
- **iOS**: iPhone 14 Pro Max (430 x 932)
- **Android**: Pixel 7 Pro (412 x 892)
- **Tests**: Layout scaling, image sizing

### Tablet (width > 500)
- **iOS**: iPad (810 x 1080)
- **Android**: Pixel Tablet (840 x 1280)
- **Tests**: Multi-column layouts, split views

---

## Device-Specific Tests

```javascript
describe('Device Matrix - Product List', () => {
  beforeAll(async () => {
    await device.launchApp()
    await loginAsTestUser()
  })

  describe('Layout Tests', () => {
    it('should display product grid correctly', async () => {
      await element(by.id('tab-products')).tap()
      await expect(element(by.id('products-grid'))).toBeVisible()
      await expect(element(by.id('product-card-0'))).toBeVisible()
    })

    it('should handle long product names', async () => {
      // Verify text truncation works
      await expect(element(by.id('product-name-long')))
        .toHaveText(expect.stringMatching(/^.{1,30}\.\.\.$/))
    })
  })

  describe('Touch Target Tests', () => {
    it('should have adequate touch targets (44x44 minimum)', async () => {
      await element(by.id('add-product-button')).tap()
      await expect(element(by.id('product-form'))).toBeVisible()
    })
  })
})
```
