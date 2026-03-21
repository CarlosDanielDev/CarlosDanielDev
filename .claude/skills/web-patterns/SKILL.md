---
name: web-patterns
version: "1.0.0"
description: React Web component patterns, hooks, routing, forms, and state management for web-app. Use when designing React Web architecture or implementing frontend features.
allowed-tools: Read, Grep, Glob, WebSearch
---

# Web Patterns Skill

**Platform**: React Web (web-app)
**Version**: 1.0.0
**Last Updated**: 2026-02-03

## Purpose

This skill provides **complete component patterns**, **hooks patterns**, **routing strategies**, and **form implementations** for React Web applications. Use this skill when architecting or implementing React Web features.

## When to Consult

**ALWAYS consult this skill when:**
- Designing React Web component architecture
- Implementing forms with react-hook-form
- Setting up routing with React Router
- Managing state with Redux Toolkit (using hooks)
- Creating context providers and custom hooks
- Implementing error boundaries
- Setting up code splitting and lazy loading

**Related Skills:**
- `web-optimization` - Performance optimization for React Web
- `shared-patterns` - TypeScript and async patterns
- `testing-patterns` - Testing strategies for React Web

## Quick Reference

### 1. Component Patterns

#### Functional Components (Default)
```typescript
import { FC } from 'react';

interface Props {
  title: string;
  onAction: () => void;
}

export const MyComponent: FC<Props> = ({ title, onAction }) => {
  return (
    <div>
      <h1>{title}</h1>
      <button onClick={onAction}>Action</button>
    </div>
  );
};
```

#### Component with State (useState)
```typescript
import { FC, useState } from 'react';

export const Counter: FC = () => {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
};
```

#### Component with Effects (useEffect)
```typescript
import { FC, useEffect, useState } from 'react';

export const DataFetcher: FC<{ userId: string }> = ({ userId }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const result = await fetch(`/api/users/${userId}`);
      setData(await result.json());
      setLoading(false);
    };

    fetchData();
  }, [userId]); // Re-run when userId changes

  if (loading) return <div>Loading...</div>;
  return <div>{JSON.stringify(data)}</div>;
};
```

**Detailed Guide**: See `component-patterns.md`

---

### 2. Custom Hooks

#### useLocalStorage Hook
```typescript
import { useState, useEffect } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}
```

#### useDebounce Hook
```typescript
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}
```

**Detailed Guide**: See `hooks-patterns.md`

---

### 3. Redux Toolkit (with Hooks)

#### Create Slice
```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface CounterState {
  value: number;
}

const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0 } as CounterState,
  reducers: {
    increment: (state) => {
      state.value += 1;
    },
    decrement: (state) => {
      state.value -= 1;
    },
    incrementByAmount: (state, action: PayloadAction<number>) => {
      state.value += action.payload;
    },
  },
});

export const { increment, decrement, incrementByAmount } = counterSlice.actions;
export default counterSlice.reducer;
```

#### Use in Component (with Hooks)
```typescript
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from './store';
import { increment, decrement } from './counterSlice';

export const Counter: FC = () => {
  const count = useSelector((state: RootState) => state.counter.value);
  const dispatch = useDispatch();

  return (
    <div>
      <p>{count}</p>
      <button onClick={() => dispatch(increment())}>+</button>
      <button onClick={() => dispatch(decrement())}>-</button>
    </div>
  );
};
```

**Detailed Guide**: See `redux-toolkit-patterns.md`

---

### 4. Forms with react-hook-form

#### Basic Form
```typescript
import { useForm } from 'react-hook-form';

interface FormData {
  email: string;
  password: string;
}

export const LoginForm: FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();

  const onSubmit = (data: FormData) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email', { required: 'Email is required' })} />
      {errors.email && <span>{errors.email.message}</span>}

      <input type="password" {...register('password', { required: true })} />
      {errors.password && <span>Password is required</span>}

      <button type="submit">Submit</button>
    </form>
  );
};
```

**Detailed Guide**: See `form-patterns.md`

---

### 5. Context API

#### Create Context
```typescript
import { createContext, useContext, FC, ReactNode } from 'react';

interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
```

**Detailed Guide**: See `context-patterns.md`

---

### 6. React Router

#### Setup Router
```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';

export const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<About />} />
      <Route path="/users/:id" element={<UserDetail />} />
    </Routes>
  </BrowserRouter>
);
```

#### Navigation
```typescript
import { useNavigate, useParams } from 'react-router-dom';

export const UserDetail: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  return (
    <div>
      <h1>User {id}</h1>
      <button onClick={() => navigate('/')}>Go Home</button>
    </div>
  );
};
```

**Detailed Guide**: See `routing-patterns.md`

---

## Detailed Guides

For complete implementations with multiple examples and best practices, consult:

| Guide | Content |
|-------|---------|
| `component-patterns.md` | Functional components, composition, render props, HOCs |
| `hooks-patterns.md` | Custom hooks, useEffect patterns, performance hooks |
| `redux-toolkit-patterns.md` | Slices, async thunks, selectors, typed hooks |
| `form-patterns.md` | react-hook-form, validation, dynamic forms |
| `context-patterns.md` | Context providers, multiple contexts, optimization |
| `routing-patterns.md` | React Router, nested routes, protected routes |

## Progressive Disclosure

This SKILL.md provides **quick reference patterns**. For detailed implementations:
1. Read this file first for overview
2. Consult specific guide files only when needed
3. Saves ~300-900 tokens per subagent invocation

## Anti-Patterns to Avoid

1. **Don't use class components** - Use functional components with hooks
2. **Don't use Redux connect()** - Use `useSelector` and `useDispatch` hooks
3. **Don't mutate state directly** - Use setState or Redux Toolkit (Immer)
4. **Don't forget dependency arrays** - Always specify useEffect dependencies
5. **Don't create context for everything** - Use only for truly global state
6. **Don't nest routes incorrectly** - Use proper Route nesting in React Router

## Best Practices

1. **Use TypeScript** - Type all props, state, and hooks
2. **Extract custom hooks** - Reuse stateful logic
3. **Code splitting** - Use React.lazy() for large components
4. **Error boundaries** - Wrap components for graceful errors
5. **Memoization** - Use useMemo/useCallback for expensive operations
6. **Accessibility** - Use semantic HTML and ARIA attributes
