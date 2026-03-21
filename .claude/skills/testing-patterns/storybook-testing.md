# Storybook Component Testing

Component testing and documentation for web-app.

---

## Story Template

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
}

export default meta
type Story = StoryObj<typeof Button>

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Button',
  },
}

export const Secondary: Story = {
  args: {
    variant: 'secondary',
    children: 'Button',
  },
}

export const Disabled: Story = {
  args: {
    disabled: true,
    children: 'Button',
  },
}
```

---

## Interaction Testing

```typescript
import { expect } from '@storybook/jest'
import { within, userEvent } from '@storybook/testing-library'

export const WithInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button')

    await userEvent.click(button)
    await expect(button).toHaveClass('active')
  },
}
```

---

## Snapshot Testing

```typescript
// Button.test.tsx
import { composeStories } from '@storybook/react'
import { render } from '@testing-library/react'
import * as stories from './Button.stories'

const { Primary, Secondary } = composeStories(stories)

test('Primary button snapshot', () => {
  const { container } = render(<Primary />)
  expect(container).toMatchSnapshot()
})
```
