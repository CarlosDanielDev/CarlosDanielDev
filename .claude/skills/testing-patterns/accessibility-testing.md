# Accessibility Testing

WCAG compliance and a11y testing for web-app.

---

## axe-core Integration

```typescript
// playwright.config.ts
import { injectAxe, checkA11y } from 'axe-playwright'

test('should have no accessibility violations', async ({ page }) => {
  await page.goto('/')
  await injectAxe(page)

  const results = await checkA11y(page)
  expect(results.violations).toEqual([])
})
```

---

## Accessibility Checklist

### Keyboard Navigation
- [ ] All interactive elements accessible via Tab
- [ ] Focus visible and logical order
- [ ] Escape key closes modals/menus
- [ ] Enter/Space activates buttons

### Screen Reader Support
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] ARIA labels on custom components
- [ ] Semantic HTML (button, nav, main, etc.)

### Color Contrast
- [ ] Text contrast ratio >= 4.5:1
- [ ] Large text contrast ratio >= 3:1
- [ ] UI components contrast >= 3:1

---

## Testing Keyboard Navigation

```typescript
test('should navigate with keyboard', async ({ page }) => {
  await page.goto('/')

  // Tab through interactive elements
  await page.keyboard.press('Tab')
  await expect(page.locator(':focus')).toHaveAttribute('data-testid', 'first-button')

  await page.keyboard.press('Tab')
  await expect(page.locator(':focus')).toHaveAttribute('data-testid', 'second-button')

  // Activate button with Enter
  await page.keyboard.press('Enter')
})
```

---

## ARIA Testing

```typescript
test('should have proper ARIA attributes', async ({ page }) => {
  await page.goto('/products')

  const button = page.locator('[data-testid="add-product"]')
  await expect(button).toHaveAttribute('aria-label', 'Add new product')

  const modal = page.locator('[role="dialog"]')
  await expect(modal).toHaveAttribute('aria-modal', 'true')
})
```
