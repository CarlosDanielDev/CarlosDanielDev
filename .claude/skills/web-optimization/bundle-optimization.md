# Bundle Optimization - web-app

## Avoid Barrel Imports

### The Problem

Barrel files (`index.ts`) that re-export everything prevent tree-shaking:

```tsx
// components/index.ts - This is a barrel file
export { Button } from './Button';
export { Input } from './Input';
export { Modal } from './Modal';
// ... 50 more components

// Usage - Imports ALL components even if you only need Button
import { Button } from './components';
```

### The Solution

```tsx
// GOOD - Direct import, only Button is bundled
import { Button } from './components/Button';

// GOOD - Or use path aliases
import { Button } from '@/components/Button';
```

### Detecting Barrel Imports

Check your bundle for unnecessary code:
```bash
# Using source-map-explorer
npx source-map-explorer build/static/js/*.js

# Using webpack-bundle-analyzer
npm run build -- --analyze
```

## Dynamic Imports (Code Splitting)

### 1. Route-Level Splitting

```tsx
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

// Split by route
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Reports = lazy(() => import('./pages/Reports'));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </Suspense>
  );
}
```

### 2. Component-Level Splitting

```tsx
// Heavy component lazy loaded
const RichTextEditor = lazy(() => import('./components/RichTextEditor'));
const ChartDashboard = lazy(() => import('./components/ChartDashboard'));
const PDFViewer = lazy(() => import('./components/PDFViewer'));

function DocumentEditor() {
  return (
    <Suspense fallback={<EditorSkeleton />}>
      <RichTextEditor />
    </Suspense>
  );
}
```

### 3. Conditional Loading

```tsx
// Load heavy features only when needed
function ProductPage({ product }) {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <ProductInfo product={product} />

      <button onClick={() => setShowChart(true)}>
        Show Analytics
      </button>

      {showChart && (
        <Suspense fallback={<ChartSkeleton />}>
          <ProductAnalytics productId={product.id} />
        </Suspense>
      )}
    </div>
  );
}
```

### 4. Named Exports with Dynamic Import

```tsx
// For named exports, use intermediate file or this pattern
const { AdvancedChart } = await import('./charts');

// Or with React.lazy
const AdvancedChart = lazy(() =>
  import('./charts').then(module => ({ default: module.AdvancedChart }))
);
```

## Defer Third-Party Scripts

### 1. Load After Initial Render

```tsx
function App() {
  useEffect(() => {
    // Wait for initial render
    const timer = setTimeout(() => {
      loadAnalytics();
      loadChatWidget();
      loadHotjar();
    }, 3000); // 3 seconds after mount

    return () => clearTimeout(timer);
  }, []);

  return <MainContent />;
}
```

### 2. Load on User Interaction

```tsx
function ChatButton() {
  const [chatLoaded, setChatLoaded] = useState(false);

  const handleClick = async () => {
    if (!chatLoaded) {
      await loadIntercom();
      setChatLoaded(true);
    }
    window.Intercom('show');
  };

  return <Button onClick={handleClick}>Chat with us</Button>;
}
```

### 3. Intersection Observer (Load on Scroll)

```tsx
function LazyWidget({ loader, children }) {
  const ref = useRef<HTMLDivElement>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !loaded) {
          loader().then(() => setLoaded(true));
          observer.disconnect();
        }
      },
      { rootMargin: '100px' }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [loader, loaded]);

  return <div ref={ref}>{loaded ? children : <Placeholder />}</div>;
}

// Usage
<LazyWidget loader={loadYouTubeAPI}>
  <YouTubeEmbed videoId="abc123" />
</LazyWidget>
```

## Preloading Critical Resources

### 1. Preload Critical Chunks

```tsx
// In index.html or via Helmet
<link rel="preload" href="/static/js/main.chunk.js" as="script" />
<link rel="preload" href="/fonts/Graphik.woff2" as="font" crossOrigin />
```

### 2. Prefetch Next Route

```tsx
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

// Prefetch likely next routes
function usePrefetch() {
  const location = useLocation();

  useEffect(() => {
    if (location.pathname === '/dashboard') {
      // User likely to visit these next
      import('./pages/Analytics');
      import('./pages/Reports');
    }
  }, [location]);
}
```

### 3. Preload on Hover

```tsx
function NavLink({ to, children }) {
  const prefetch = () => {
    // Preload the route when user hovers
    switch (to) {
      case '/settings':
        import('./pages/Settings');
        break;
      case '/analytics':
        import('./pages/Analytics');
        break;
    }
  };

  return (
    <Link to={to} onMouseEnter={prefetch}>
      {children}
    </Link>
  );
}
```

## Image Optimization

### 1. Lazy Load Images

```tsx
function LazyImage({ src, alt, ...props }) {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      {...props}
    />
  );
}
```

### 2. Responsive Images

```tsx
function ResponsiveImage({ src, alt }) {
  return (
    <picture>
      <source
        media="(max-width: 768px)"
        srcSet={`${src}?w=400 1x, ${src}?w=800 2x`}
      />
      <source
        media="(min-width: 769px)"
        srcSet={`${src}?w=800 1x, ${src}?w=1600 2x`}
      />
      <img src={src} alt={alt} loading="lazy" />
    </picture>
  );
}
```

### 3. WebP with Fallback

```tsx
function OptimizedImage({ src, alt }) {
  const webpSrc = src.replace(/\.(jpg|png)$/, '.webp');

  return (
    <picture>
      <source srcSet={webpSrc} type="image/webp" />
      <img src={src} alt={alt} loading="lazy" />
    </picture>
  );
}
```

## CRACO Configuration (web-app)

### 1. Bundle Analyzer

```javascript
// craco.config.js
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = {
  webpack: {
    plugins: {
      add: process.env.ANALYZE
        ? [new BundleAnalyzerPlugin()]
        : [],
    },
  },
};
```

### 2. Split Chunks Configuration

```javascript
// craco.config.js
module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      webpackConfig.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            name: 'vendors',
            test: /[\\/]node_modules[\\/]/,
            priority: 10,
          },
          vendor: {
            name: 'ui',
            test: /[\\/]@company[\\/]/,
            priority: 20,
          },
        },
      };
      return webpackConfig;
    },
  },
};
```

### 3. Compression

```javascript
// craco.config.js
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  webpack: {
    plugins: {
      add: [
        new CompressionPlugin({
          algorithm: 'gzip',
          test: /\.(js|css|html|svg)$/,
          threshold: 10240,
          minRatio: 0.8,
        }),
      ],
    },
  },
};
```

## Measuring Bundle Size

```bash
# Check bundle size
npm run build

# With source map explorer
npx source-map-explorer build/static/js/*.js

# With bundle analyzer
ANALYZE=true npm run build

# Check specific package impact
npx import-cost
```

## Bundle Size Targets

| Metric | Target | Critical |
|--------|--------|----------|
| Main bundle | < 200 KB (gzipped) | < 500 KB |
| Initial CSS | < 50 KB (gzipped) | < 100 KB |
| First Contentful Paint | < 1.5s | < 3s |
| Time to Interactive | < 3s | < 5s |
