# Mobile Performance Testing

Performance metrics and thresholds for mobile-app.

---

## Performance Thresholds

| Metric | Threshold | Action if Exceeded |
|--------|-----------|-------------------|
| App startup | < 3s | CONCERNS |
| Screen load | < 2s | CONCERNS |
| Login flow | < 5s | CONCERNS |
| App startup | > 5s | FAIL |
| Screen load | > 4s | FAIL |

---

## Startup Time Test

```javascript
// e2e/performance/startup.e2e.js
describe('Performance - Startup Time', () => {
  it('should launch app under 3 seconds', async () => {
    const startTime = Date.now()

    await device.launchApp({ newInstance: true })
    await waitFor(element(by.id('app-ready')))
      .toBeVisible()
      .withTimeout(10000)

    const launchTime = Date.now() - startTime
    console.log(`App launch time: ${launchTime}ms`)

    expect(launchTime).toBeLessThan(3000)
  })
})
```

---

## Screen Load Performance

```javascript
describe('Performance - Screen Load Times', () => {
  const screens = [
    { id: 'products-list', name: 'Products', threshold: 2000 },
    { id: 'dashboard-screen', name: 'Dashboard', threshold: 1500 },
  ]

  beforeAll(async () => {
    await device.launchApp()
    await loginAsTestUser()
  })

  for (const screen of screens) {
    it(`should load ${screen.name} under ${screen.threshold}ms`, async () => {
      const startTime = Date.now()

      await element(by.id(`tab-${screen.name.toLowerCase()}`)).tap()
      await waitFor(element(by.id(screen.id)))
        .toBeVisible()
        .withTimeout(10000)

      const loadTime = Date.now() - startTime
      console.log(`${screen.name} load time: ${loadTime}ms`)

      expect(loadTime).toBeLessThan(screen.threshold)
    })
  }
})
```
