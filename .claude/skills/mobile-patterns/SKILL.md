---
name: mobile-patterns
version: "1.0.0"
description: React Native patterns including Redux connect(), component structure, navigation, forms, and mobile best practices. Use when analyzing or implementing mobile features.
allowed-tools: Read, Grep, Glob, WebSearch
---

# Mobile Patterns (React Native)

Quick reference for React Native patterns. For detailed examples, see linked guides.

## Skill Usage

| Aspect | Details |
|--------|---------|
| **Consumer** | `subagent-mobile-architect` |
| **Purpose** | Code patterns and examples for mobile implementation |
| **Invocation** | Subagents read this skill; NOT directly invocable by users |
| **Related Skills** | `mobile-optimization`, `shared-patterns`, `testing-patterns` |

---

## Critical Stack Requirements

| Feature | Pattern | NOT Allowed |
|---------|---------|-------------|
| **State** | Redux with `connect()` | Redux hooks (useSelector, useDispatch) ❌ |
| **Forms** | `redux-form` with Field | react-hook-form ❌ |
| **Files** | `.tsx` for new files | `.js` for new files ❌ |
| **UI** | `@company/ui-components` | Custom native components |
| **Navigation** | React Navigation | Other navigation libs |

---

## Quick Patterns Reference

### Redux Connection (CRITICAL)

```typescript
// ✅ CORRECT - Use connect()
import { connect } from 'react-redux'
import { someAction } from '../stores/actions'

const MyComponent = ({ user, someAction }) => {
  // Props from mapStateToProps/mapDispatchToProps
}

const mapStateToProps = (state: RootState) => ({
  user: state.auth.user,
})

const mapDispatchToProps = { someAction }

export default connect(mapStateToProps, mapDispatchToProps)(MyComponent)
```

❌ **NEVER use Redux hooks** (useSelector, useDispatch)

### Component Structure

```typescript
import React from 'react'
import { Container, Text } from '@company/ui-components'
import { connect } from 'react-redux'
import { generateTestID } from '../../util'

const MyComponent: React.FC<Props> = ({ user, navigation }) => (
  <Container padding={20}>
    <Text {...generateTestID('title')}>Hello {user.name}</Text>
  </Container>
)

const mapStateToProps = (state: RootState) => ({
  user: state.auth.user,
})

export default connect(mapStateToProps)(MyComponent)
```

### Test IDs (MANDATORY)

```typescript
import { generateTestID } from '../../util'

// Every interactive element MUST have testID
<Button {...generateTestID('save-button')} onPress={handleSave}>
  Save
</Button>
```

---

## Detailed Guides

When you need specific implementation details, read:

- **[redux-patterns.md](redux-patterns.md)** - Complete Redux patterns
  - Actions, reducers, async thunks
  - Selectors and state management
  - redux-form integration

- **[component-templates.md](component-templates.md)** - Component boilerplates
  - Screen component template
  - Modal component template
  - List item template

- **[navigation-patterns.md](navigation-patterns.md)** - Navigation setup
  - Stack navigator config
  - Tab navigation
  - Deep linking

- **[forms-patterns.md](forms-patterns.md)** - Form handling
  - redux-form setup
  - Field components
  - Validation

- **[common-components.md](common-components.md)** - Reusable components
  - Screen component usage
  - Modal component patterns
  - UI library components

- **[platform-specific.md](platform-specific.md)** - iOS/Android differences
  - Platform.select() usage
  - Safe areas
  - Gesture handling

- **[i18n-patterns.md](i18n-patterns.md)** - Internationalization
  - I18n setup
  - Translation strings
  - Language switching

---

## Common Anti-Patterns to Avoid

1. ❌ Using `useSelector`/`useDispatch` instead of `connect()`
2. ❌ Creating new `.js` files (use `.tsx`)
3. ❌ Inline functions in JSX props
4. ❌ Missing `testID` on interactive elements
5. ❌ Using ScrollView for long lists (use FlatList)
6. ❌ Fetching data in render method
7. ❌ Not cleaning up subscriptions on unmount

---

## Dependencies Reference

```json
{
  "react-native": "Core framework",
  "redux": "State management (with connect)",
  "redux-form": "Form handling",
  "react-native-i18n": "Internationalization",
  "@company/ui-components": "UI library",
  "@react-navigation/native": "Navigation",
  "mixpanel-react-native": "Analytics",
  "@react-native-firebase/analytics": "Firebase",
  "detox": "E2E testing"
}
```

---

## When to Consult This Skill

- Designing mobile component architecture
- Implementing Redux patterns for mobile
- Creating forms in React Native
- Setting up navigation flows
- Implementing platform-specific features
- Adding analytics tracking
- Creating testable mobile components
