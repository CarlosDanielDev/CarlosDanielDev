# Playwright Visual Regression Testing

Visual testing and Figma design comparison for web-app.

---

## Visual Testing Setup

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    screenshot: 'on',
  },
})
```

---

## Screenshot Testing

```typescript
test('should match homepage screenshot', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveScreenshot('homepage.png')
})

test('should match product card', async ({ page }) => {
  await page.goto('/products')
  const card = page.locator('[data-testid="product-card-0"]')
  await expect(card).toHaveScreenshot('product-card.png')
})
```

---

## Figma Design Comparison

**Goal**: 95% visual similarity with Figma designs

**Workflow**:
1. Export design from Figma as PNG
2. Take screenshot of implementation
3. Compare using visual diff tool
4. Report similarity percentage

```typescript
import pixelmatch from 'pixelmatch'
import { PNG } from 'pngjs'

test('should match Figma design', async ({ page }) => {
  await page.goto('/products')

  // Take screenshot
  const screenshot = await page.screenshot()

  // Load Figma design
  const figmaDesign = PNG.sync.read(fs.readFileSync('designs/products.png'))
  const implScreenshot = PNG.sync.read(screenshot)

  // Compare
  const diff = new PNG({ width: figmaDesign.width, height: figmaDesign.height })
  const numDiffPixels = pixelmatch(
    figmaDesign.data,
    implScreenshot.data,
    diff.data,
    figmaDesign.width,
    figmaDesign.height,
    { threshold: 0.1 }
  )

  const similarity = 1 - (numDiffPixels / (figmaDesign.width * figmaDesign.height))
  expect(similarity).toBeGreaterThan(0.95) // 95% similarity
})
```

---

## Visual Diff Baseline

```bash
# Generate baseline screenshots
npx playwright test --update-snapshots

# Compare against baseline
npx playwright test
```
