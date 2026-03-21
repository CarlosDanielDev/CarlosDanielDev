# Component Patterns for React Web

**Platform**: React Web (web-app)
**Last Updated**: 2026-02-03

## Overview

This guide provides comprehensive component patterns for React Web applications using functional components and hooks.

## 1. Basic Functional Component

### Simple Component
```typescript
import { FC } from 'react';

interface Props {
  title: string;
  description?: string;
}

export const SimpleCard: FC<Props> = ({ title, description }) => {
  return (
    <div className="card">
      <h2>{title}</h2>
      {description && <p>{description}</p>}
    </div>
  );
};
```

### Component with Children
```typescript
import { FC, ReactNode } from 'react';

interface Props {
  title: string;
  children: ReactNode;
}

export const Container: FC<Props> = ({ title, children }) => {
  return (
    <div className="container">
      <h1>{title}</h1>
      <div className="content">{children}</div>
    </div>
  );
};

// Usage
<Container title="My App">
  <p>This is the content</p>
</Container>
```

---

## 2. Component Composition

### Compound Components
```typescript
import { FC, ReactNode, createContext, useContext } from 'react';

interface TabsContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextType | undefined>(undefined);

export const Tabs: FC<{ children: ReactNode; defaultTab: string }> = ({
  children,
  defaultTab,
}) => {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
};

export const TabList: FC<{ children: ReactNode }> = ({ children }) => {
  return <div className="tab-list">{children}</div>;
};

export const Tab: FC<{ value: string; children: ReactNode }> = ({
  value,
  children,
}) => {
  const context = useContext(TabsContext);
  if (!context) throw new Error('Tab must be used within Tabs');

  const { activeTab, setActiveTab } = context;

  return (
    <button
      className={activeTab === value ? 'active' : ''}
      onClick={() => setActiveTab(value)}
    >
      {children}
    </button>
  );
};

export const TabPanel: FC<{ value: string; children: ReactNode }> = ({
  value,
  children,
}) => {
  const context = useContext(TabsContext);
  if (!context) throw new Error('TabPanel must be used within Tabs');

  const { activeTab } = context;

  if (activeTab !== value) return null;

  return <div className="tab-panel">{children}</div>;
};

// Usage
<Tabs defaultTab="home">
  <TabList>
    <Tab value="home">Home</Tab>
    <Tab value="profile">Profile</Tab>
  </TabList>

  <TabPanel value="home">
    <p>Home content</p>
  </TabPanel>

  <TabPanel value="profile">
    <p>Profile content</p>
  </TabPanel>
</Tabs>
```

---

## 3. Higher-Order Components (HOCs)

### withLoading HOC
```typescript
import { FC, ComponentType } from 'react';

interface WithLoadingProps {
  loading: boolean;
}

export function withLoading<P extends object>(
  Component: ComponentType<P>
): FC<P & WithLoadingProps> {
  return ({ loading, ...props }: WithLoadingProps) => {
    if (loading) {
      return <div>Loading...</div>;
    }

    return <Component {...(props as P)} />;
  };
}

// Usage
const UserProfile: FC<{ name: string }> = ({ name }) => <div>{name}</div>;

const UserProfileWithLoading = withLoading(UserProfile);

// Render
<UserProfileWithLoading loading={isLoading} name="John" />
```

### withAuth HOC
```typescript
import { FC, ComponentType } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function withAuth<P extends object>(
  Component: ComponentType<P>
): FC<P> {
  return (props: P) => {
    const { isAuthenticated } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
      if (!isAuthenticated) {
        navigate('/login');
      }
    }, [isAuthenticated, navigate]);

    if (!isAuthenticated) {
      return null;
    }

    return <Component {...props} />;
  };
}

// Usage
const Dashboard: FC = () => <div>Dashboard</div>;

const ProtectedDashboard = withAuth(Dashboard);
```

---

## 4. Render Props Pattern

```typescript
import { FC, ReactNode } from 'react';

interface MousePosition {
  x: number;
  y: number;
}

interface Props {
  children: (position: MousePosition) => ReactNode;
}

export const MouseTracker: FC<Props> = ({ children }) => {
  const [position, setPosition] = useState<MousePosition>({ x: 0, y: 0 });

  const handleMouseMove = (event: MouseEvent) => {
    setPosition({ x: event.clientX, y: event.clientY });
  };

  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return <>{children(position)}</>;
};

// Usage
<MouseTracker>
  {({ x, y }) => (
    <div>
      Mouse position: {x}, {y}
    </div>
  )}
</MouseTracker>
```

---

## 5. Error Boundaries

```typescript
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <h1>Something went wrong.</h1>;
    }

    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<div>Error occurred</div>}>
  <MyComponent />
</ErrorBoundary>
```

---

## 6. Lazy Loading and Code Splitting

```typescript
import { lazy, Suspense } from 'react';

// Lazy load component
const LazyComponent = lazy(() => import('./LazyComponent'));

export const App: FC = () => {
  return (
    <Suspense fallback={<div>Loading component...</div>}>
      <LazyComponent />
    </Suspense>
  );
};
```

### Route-based Code Splitting
```typescript
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

export const App: FC = () => {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading page...</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
};
```

---

## 7. Performance Optimization

### React.memo
```typescript
import { FC, memo } from 'react';

interface Props {
  title: string;
  count: number;
}

// Component will only re-render if props change
export const ExpensiveComponent: FC<Props> = memo(({ title, count }) => {
  console.log('Rendering ExpensiveComponent');

  return (
    <div>
      <h1>{title}</h1>
      <p>Count: {count}</p>
    </div>
  );
});

// Custom comparison function
export const CustomMemoComponent = memo(
  ({ data }: { data: { id: string; name: string } }) => {
    return <div>{data.name}</div>;
  },
  (prevProps, nextProps) => {
    // Return true if props are equal (don't re-render)
    return prevProps.data.id === nextProps.data.id;
  }
);
```

### useMemo and useCallback
```typescript
import { FC, useMemo, useCallback } from 'react';

export const OptimizedComponent: FC<{ items: string[] }> = ({ items }) => {
  // Memoize expensive computation
  const sortedItems = useMemo(() => {
    console.log('Sorting items...');
    return items.sort();
  }, [items]);

  // Memoize callback function
  const handleClick = useCallback(() => {
    console.log('Clicked');
  }, []);

  return (
    <div>
      {sortedItems.map((item) => (
        <div key={item} onClick={handleClick}>
          {item}
        </div>
      ))}
    </div>
  );
};
```

---

## 8. Controlled vs Uncontrolled Components

### Controlled Component
```typescript
export const ControlledInput: FC = () => {
  const [value, setValue] = useState('');

  return (
    <input
      type="text"
      value={value}
      onChange={(e) => setValue(e.target.value)}
    />
  );
};
```

### Uncontrolled Component
```typescript
import { useRef } from 'react';

export const UncontrolledInput: FC = () => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    if (inputRef.current) {
      console.log(inputRef.current.value);
    }
  };

  return (
    <div>
      <input type="text" ref={inputRef} />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
};
```

---

## Best Practices

1. **Prefer functional components** over class components
2. **Use TypeScript** for type safety
3. **Extract reusable logic** into custom hooks
4. **Compose components** instead of creating monolithic components
5. **Use React.memo** for expensive components that receive same props
6. **Lazy load** large components and routes
7. **Use Error Boundaries** to prevent entire app crashes
8. **Keep components small** (< 200 lines)
9. **Single Responsibility** - one component, one purpose

## Anti-Patterns to Avoid

1. ❌ **Don't use class components** - Use functional components
2. ❌ **Don't mutate props** - Props are immutable
3. ❌ **Don't forget keys in lists** - Always provide unique keys
4. ❌ **Don't use index as key** - Use stable, unique identifiers
5. ❌ **Don't overuse HOCs** - Prefer hooks and composition
6. ❌ **Don't create unnecessary contexts** - Use only for global state
7. ❌ **Don't nest ternaries** - Extract to variables or components
