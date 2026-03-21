# Rendering Optimization - web-app

## Preventing Re-renders

### 1. React.memo for List Items

```tsx
// BAD - Re-renders every item when list changes
function ProductList({ products }) {
  return products.map(product => (
    <ProductCard key={product.id} product={product} />
  ));
}

// GOOD - Only re-render items that changed
const ProductCard = memo(({ product }: { product: Product }) => {
  return (
    <div className="product-card">
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p>{product.price}</p>
    </div>
  );
});

// With custom comparison for complex props
const ProductCard = memo(
  ({ product }) => <div>{/* ... */}</div>,
  (prevProps, nextProps) =>
    prevProps.product.id === nextProps.product.id &&
    prevProps.product.updatedAt === nextProps.product.updatedAt
);
```

### 2. Avoid Inline Objects/Functions

```tsx
// BAD - New object/function every render
function UserProfile({ user }) {
  return (
    <Card
      style={{ margin: 10 }} // New object every render
      onClick={() => console.log(user.id)} // New function every render
    >
      {user.name}
    </Card>
  );
}

// GOOD - Stable references
const cardStyle = { margin: 10 };

function UserProfile({ user }) {
  const handleClick = useCallback(() => {
    console.log(user.id);
  }, [user.id]);

  return (
    <Card style={cardStyle} onClick={handleClick}>
      {user.name}
    </Card>
  );
}
```

### 3. useMemo for Expensive Computations

```tsx
function ProductTable({ products, sortBy, filterBy }) {
  // Memoize expensive filtering/sorting
  const processedProducts = useMemo(() => {
    console.log('Processing products...'); // Only logs when deps change

    return products
      .filter(p => p.category === filterBy)
      .sort((a, b) => a[sortBy] - b[sortBy]);
  }, [products, sortBy, filterBy]);

  return (
    <table>
      {processedProducts.map(product => (
        <ProductRow key={product.id} product={product} />
      ))}
    </table>
  );
}
```

## React 18 Concurrent Features

### 1. useTransition for Non-Urgent Updates

```tsx
function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;

    // Urgent: Update input immediately
    setQuery(value);

    // Non-urgent: Can be interrupted
    startTransition(() => {
      const filtered = searchProducts(value);
      setResults(filtered);
    });
  };

  return (
    <div>
      <input value={query} onChange={handleSearch} />
      {isPending && <Spinner />}
      <ProductList products={results} />
    </div>
  );
}
```

### 2. useDeferredValue for Derived State

```tsx
function ProductGrid({ products }) {
  const [filter, setFilter] = useState('');

  // Defer the filtered value
  const deferredFilter = useDeferredValue(filter);

  // Use deferred value for expensive computation
  const filteredProducts = useMemo(
    () => products.filter(p => p.name.includes(deferredFilter)),
    [products, deferredFilter]
  );

  const isStale = filter !== deferredFilter;

  return (
    <div>
      <input
        value={filter}
        onChange={e => setFilter(e.target.value)}
      />
      <div style={{ opacity: isStale ? 0.7 : 1 }}>
        <Grid items={filteredProducts} />
      </div>
    </div>
  );
}
```

### 3. Suspense for Data Loading

```tsx
// With RTK Query or React Query
function UserProfile({ userId }) {
  return (
    <Suspense fallback={<ProfileSkeleton />}>
      <UserDetails userId={userId} />
    </Suspense>
  );
}

// UserDetails suspends until data is ready
function UserDetails({ userId }) {
  // This hook suspends the component
  const { data: user } = useGetUserQuery(userId, { suspense: true });

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

## CSS Performance

### 1. content-visibility for Long Lists

```css
/* Hide off-screen content from rendering */
.list-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 100px; /* Estimated height */
}

/* Skip rendering entirely when off-screen */
.heavy-section {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px;
}
```

```tsx
// Usage in React
function LongList({ items }) {
  return (
    <div className="list">
      {items.map(item => (
        <div key={item.id} className="list-item">
          <ItemContent item={item} />
        </div>
      ))}
    </div>
  );
}
```

### 2. will-change for Animations

```css
/* Tell browser to optimize for transform/opacity changes */
.animated-card {
  will-change: transform, opacity;
}

/* Remove after animation to free resources */
.animated-card.animation-complete {
  will-change: auto;
}
```

### 3. CSS containment

```css
/* Isolate layout calculations */
.widget {
  contain: layout style paint;
}

/* Full isolation for independent components */
.independent-section {
  contain: strict;
}
```

## Hoist Static JSX

### 1. Move Static Content Outside Component

```tsx
// BAD - Created every render
function ProductPage() {
  const header = (
    <header>
      <h1>Products</h1>
      <p>Browse our catalog</p>
    </header>
  );

  return (
    <div>
      {header}
      <ProductList />
    </div>
  );
}

// GOOD - Created once
const PageHeader = (
  <header>
    <h1>Products</h1>
    <p>Browse our catalog</p>
  </header>
);

function ProductPage() {
  return (
    <div>
      {PageHeader}
      <ProductList />
    </div>
  );
}
```

### 2. Static Configuration Objects

```tsx
// BAD - New array every render
function DataTable({ data }) {
  return (
    <Table
      columns={[
        { key: 'name', label: 'Name' },
        { key: 'price', label: 'Price' },
        { key: 'stock', label: 'Stock' },
      ]}
      data={data}
    />
  );
}

// GOOD - Defined once
const TABLE_COLUMNS = [
  { key: 'name', label: 'Name' },
  { key: 'price', label: 'Price' },
  { key: 'stock', label: 'Stock' },
];

function DataTable({ data }) {
  return <Table columns={TABLE_COLUMNS} data={data} />;
}
```

## SVG Optimization

### 1. Reduce Precision

```xml
<!-- BAD - Too much precision -->
<path d="M12.34567890 45.67890123 L98.76543210 54.32109876" />

<!-- GOOD - Reasonable precision (2 decimal places) -->
<path d="M12.35 45.68 L98.77 54.32" />
```

### 2. Use viewBox for Scaling

```tsx
// GOOD - Scales without distortion
<svg viewBox="0 0 24 24" width="48" height="48">
  <path d="..." />
</svg>
```

### 3. Inline Critical SVGs

```tsx
// For frequently used icons, inline them
function CheckIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24">
      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
    </svg>
  );
}

// For rarely used SVGs, lazy load
const RareIcon = lazy(() => import('./icons/RareIcon'));
```

## Virtualization for Long Lists

### 1. react-window for Simple Lists

```tsx
import { FixedSizeList } from 'react-window';

function VirtualizedList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ProductCard product={items[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      width="100%"
      itemCount={items.length}
      itemSize={100}
    >
      {Row}
    </FixedSizeList>
  );
}
```

### 2. react-window for Variable Height

```tsx
import { VariableSizeList } from 'react-window';

function VirtualizedList({ items }) {
  const getItemSize = (index: number) => {
    return items[index].hasImage ? 200 : 80;
  };

  return (
    <VariableSizeList
      height={600}
      width="100%"
      itemCount={items.length}
      itemSize={getItemSize}
    >
      {Row}
    </VariableSizeList>
  );
}
```

## Debugging Re-renders

### 1. React DevTools Profiler

```tsx
// Enable in development
<React.Profiler id="ProductList" onRender={onRenderCallback}>
  <ProductList products={products} />
</React.Profiler>

function onRenderCallback(
  id,
  phase,
  actualDuration,
  baseDuration,
  startTime,
  commitTime
) {
  console.log(`${id} ${phase}: ${actualDuration}ms`);
}
```

### 2. Why Did You Render

```tsx
// Install: npm install @welldone-software/why-did-you-render

// In index.tsx (development only)
if (process.env.NODE_ENV === 'development') {
  const whyDidYouRender = require('@welldone-software/why-did-you-render');
  whyDidYouRender(React, {
    trackAllPureComponents: true,
  });
}

// Mark specific components
ProductCard.whyDidYouRender = true;
```
