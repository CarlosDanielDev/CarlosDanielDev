---
name: mobile-optimization
version: "1.0.0"
description: Optimize React Native performance in mobile-app. Use when improving startup time, reducing re-renders, optimizing navigation, working with Redux connect(), or improving FlatList performance.
allowed-tools: Read, Grep, Glob, WebSearch
---

# Mobile Optimization

Performance optimization patterns for React Native in mobile-app.

## Skill Usage

| Aspect | Details |
|--------|---------|
| **Consumer** | `subagent-mobile-architect` |
| **Purpose** | Consulted during mobile architecture analysis and implementation planning |
| **Invocation** | Subagents read this skill; NOT directly invocable by users |
| **Related Skills** | `shared-patterns` (TypeScript/async patterns) |

## Critical Stack Requirements

| Feature | Pattern | NOT Allowed |
|---------|---------|-------------|
| State | Redux with `connect()` | Redux hooks (useSelector, useDispatch) |
| Forms | `redux-form` with Field | react-hook-form |
| UI | `@company/ui-components` | Custom native components |
| Navigation | React Navigation | React Native Navigation |

## Quick Performance Wins

### 1. Avoid Inline Objects/Arrays

```tsx
// BAD - Creates new object every render
<UserList style={{ marginTop: 10 }} data={users.filter(u => u.active)} />

// GOOD - Memoize or define outside
const styles = StyleSheet.create({ container: { marginTop: 10 } });
const activeUsers = useMemo(() => users.filter(u => u.active), [users]);
<UserList style={styles.container} data={activeUsers} />
```

### 2. Use Selective mapStateToProps

```tsx
// BAD - Subscribes to entire store
const mapStateToProps = state => ({ state });

// GOOD - Select only needed data
const mapStateToProps = state => ({
  userName: state.user.name,
  isLoading: state.user.loading,
});
```

### 3. FlatList Optimization

```tsx
<FlatList
  data={items}
  keyExtractor={item => item.id}
  getItemLayout={(_, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  windowSize={5}
  initialNumToRender={10}
/>
```

## Detailed Guides

- [Performance](performance.md) - Re-renders, memoization, FlatList
- [Redux Patterns](redux-patterns.md) - connect(), selectors, redux-form
- [Navigation](navigation.md) - Lazy screens, preloading, deep linking

## Common Anti-Patterns

1. Using `useSelector`/`useDispatch` (use `connect()` instead)
2. Inline functions in JSX props
3. Missing `keyExtractor` in FlatList
4. Fetching data in render method
5. Not using `shouldComponentUpdate` or `React.memo`
