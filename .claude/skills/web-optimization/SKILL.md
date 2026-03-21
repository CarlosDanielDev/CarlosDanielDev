---
name: web-optimization
version: "1.0.0"
description: Optimize React Web performance in web-app. Use when improving bundle size, code splitting, reducing re-renders, optimizing images, working with Redux Toolkit, or implementing lazy loading.
allowed-tools: Read, Grep, Glob, WebSearch
---

# Web Optimization

Performance optimization patterns for React Web in web-app.

## Skill Usage

| Aspect | Details |
|--------|---------|
| **Consumer** | `subagent-frontend-architect` |
| **Purpose** | Consulted during web frontend architecture analysis and implementation planning |
| **Invocation** | Subagents read this skill; NOT directly invocable by users |
| **Related Skills** | `shared-patterns` (TypeScript/async patterns) |

## Critical Stack Requirements

| Feature | Pattern | Notes |
|---------|---------|-------|
| State | Redux Toolkit with slices | `{feature}.slice.ts` |
| Forms | `react-hook-form` | ControlledField pattern |
| UI | `@company/ui-components/web` | Design tokens |
| Build | CRACO | Custom webpack config |

## Quick Performance Wins

### 1. Avoid Barrel Imports

```tsx
// BAD - Imports entire library
import { Button, Input, Modal } from '@company/ui-components';

// GOOD - Direct imports
import { Button } from '@company/ui-components/web/Button';
import { Input } from '@company/ui-components/web/Input';
```

### 2. Code Splitting with React.lazy

```tsx
// Lazy load non-critical routes
const Settings = lazy(() => import('./pages/Settings'));
const Analytics = lazy(() => import('./pages/Analytics'));

<Suspense fallback={<PageSkeleton />}>
  <Routes>
    <Route path="/settings" element={<Settings />} />
    <Route path="/analytics" element={<Analytics />} />
  </Routes>
</Suspense>
```

### 3. Defer Third-Party Scripts

```tsx
// Load analytics after initial render
useEffect(() => {
  const timer = setTimeout(() => {
    loadAnalytics();
    loadIntercom();
  }, 3000);
  return () => clearTimeout(timer);
}, []);
```

## Detailed Guides

- [Bundle Optimization](bundle-optimization.md) - Tree shaking, code splitting, dynamic imports
- [Rendering](rendering.md) - Re-renders, transitions, content-visibility
- [State Management](state-management.md) - Redux Toolkit, RTK Query, react-hook-form

## Key Anti-Patterns

1. Barrel imports (`index.ts` re-exports)
2. Inline objects in JSX props
3. Missing `React.memo` on list items
4. Loading all routes upfront
5. Blocking third-party scripts
