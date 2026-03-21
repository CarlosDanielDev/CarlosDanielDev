# Async Patterns

## Parallel vs Sequential Execution

### 1. Use Promise.all for Independent Requests

```typescript
// BAD - Sequential (slower)
async function fetchDashboardData() {
  const users = await fetchUsers();        // 200ms
  const products = await fetchProducts();  // 300ms
  const orders = await fetchOrders();      // 250ms
  return { users, products, orders };      // Total: 750ms
}

// GOOD - Parallel (faster)
async function fetchDashboardData() {
  const [users, products, orders] = await Promise.all([
    fetchUsers(),    // 200ms
    fetchProducts(), // 300ms
    fetchOrders(),   // 250ms
  ]);
  return { users, products, orders }; // Total: 300ms (max of all)
}
```

### 2. Use Promise.allSettled When Partial Failure is OK

```typescript
// When some requests can fail without breaking the whole operation
async function fetchUserProfiles(userIds: string[]) {
  const results = await Promise.allSettled(
    userIds.map(id => fetchUser(id))
  );

  return results
    .filter((r): r is PromiseFulfilledResult<User> => r.status === 'fulfilled')
    .map(r => r.value);
}
```

### 3. Batch Operations with Concurrency Limit

```typescript
// Process items in batches to avoid overwhelming the server
async function processBatched<T, R>(
  items: T[],
  processor: (item: T) => Promise<R>,
  batchSize = 5
): Promise<R[]> {
  const results: R[] = [];

  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map(processor));
    results.push(...batchResults);
  }

  return results;
}

// Usage
const users = await processBatched(userIds, fetchUser, 10);
```

## Cancellation with AbortController

### 1. Basic Cancellation

```typescript
// Create controller
const controller = new AbortController();

// Pass signal to fetch
const response = await fetch('/api/users', {
  signal: controller.signal
});

// Cancel the request
controller.abort();
```

### 2. React Hook with Cancellation

```typescript
// For web-app with hooks
function useAsyncData<T>(fetcher: (signal: AbortSignal) => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    setLoading(true);
    fetcher(controller.signal)
      .then(setData)
      .catch(err => {
        if (err.name !== 'AbortError') {
          setError(err);
        }
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [fetcher]);

  return { data, loading, error };
}
```

### 3. Redux-Thunk with Cancellation (mobile-app)

```typescript
// For mobile-app with redux-thunk
let currentAbortController: AbortController | null = null;

export const fetchUsers = () => async (dispatch: Dispatch) => {
  // Cancel previous request
  if (currentAbortController) {
    currentAbortController.abort();
  }

  currentAbortController = new AbortController();

  try {
    dispatch({ type: 'FETCH_USERS_START' });
    const response = await fetch('/api/users', {
      signal: currentAbortController.signal
    });
    const users = await response.json();
    dispatch({ type: 'FETCH_USERS_SUCCESS', payload: users });
  } catch (error) {
    if (error.name !== 'AbortError') {
      dispatch({ type: 'FETCH_USERS_ERROR', payload: error });
    }
  }
};
```

## Retry Patterns

### 1. Exponential Backoff

```typescript
async function fetchWithRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
  } = {}
): Promise<T> {
  const { maxRetries = 3, baseDelay = 1000, maxDelay = 30000 } = options;

  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      if (attempt === maxRetries) break;

      // Exponential backoff with jitter
      const delay = Math.min(
        baseDelay * Math.pow(2, attempt) + Math.random() * 1000,
        maxDelay
      );

      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError!;
}

// Usage
const data = await fetchWithRetry(() => fetch('/api/unstable-endpoint'));
```

### 2. Retry Only Specific Errors

```typescript
function isRetryableError(error: unknown): boolean {
  if (error instanceof Error) {
    // Network errors
    if (error.message.includes('network') ||
        error.message.includes('timeout')) {
      return true;
    }
  }

  // HTTP status codes that should be retried
  if (error && typeof error === 'object' && 'status' in error) {
    const status = (error as { status: number }).status;
    return status === 429 || status >= 500;
  }

  return false;
}

async function fetchWithSelectiveRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      if (!isRetryableError(error) || attempt === maxRetries) {
        throw error;
      }

      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, attempt)));
    }
  }

  throw lastError!;
}
```

## Timeout Patterns

### 1. Promise with Timeout

```typescript
function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  errorMessage = 'Operation timed out'
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error(errorMessage)), timeoutMs)
    )
  ]);
}

// Usage
const data = await withTimeout(fetchUser(id), 5000, 'User fetch timed out');
```

### 2. AbortController with Timeout

```typescript
async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs = 5000
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}
```

## Error Boundaries (React)

### web-app (Class Component)

```typescript
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Report to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}
```

### mobile-app (Class Component - Required)

```typescript
// mobile-app uses class components with connect()
class AsyncErrorBoundary extends Component<Props, State> {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to crash reporting (Sentry, Crashlytics)
    logError(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <ErrorView
          error={this.state.error}
          onRetry={this.handleRetry}
        />
      );
    }
    return this.props.children;
  }
}

export default connect()(AsyncErrorBoundary);
```
