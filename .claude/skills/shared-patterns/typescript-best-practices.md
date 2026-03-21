# TypeScript Best Practices

## Type Safety Patterns

### 1. Prefer Type Narrowing Over Casting

```typescript
// BAD - Type assertion without validation
function getUser(data: unknown): User {
  return data as User; // Dangerous!
}

// GOOD - Type guard with validation
function isUser(data: unknown): data is User {
  return (
    typeof data === 'object' &&
    data !== null &&
    'id' in data &&
    'name' in data
  );
}

function getUser(data: unknown): User | null {
  if (isUser(data)) {
    return data; // TypeScript knows this is User
  }
  return null;
}
```

### 2. Use Discriminated Unions for State

```typescript
// BAD - Optional properties lead to invalid states
interface LoadingState {
  isLoading?: boolean;
  data?: User;
  error?: Error;
}

// GOOD - Discriminated union prevents invalid states
type LoadingState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: User }
  | { status: 'error'; error: Error };

// Usage with exhaustive checks
function renderState(state: LoadingState) {
  switch (state.status) {
    case 'idle':
      return null;
    case 'loading':
      return <Spinner />;
    case 'success':
      return <UserCard user={state.data} />;
    case 'error':
      return <ErrorMessage error={state.error} />;
    default:
      // Exhaustive check - TypeScript will error if a case is missing
      const _exhaustive: never = state;
      return _exhaustive;
  }
}
```

### 3. Utility Types for DRY Code

```typescript
// Pick only needed properties
type UserSummary = Pick<User, 'id' | 'name' | 'avatar'>;

// Omit sensitive properties
type PublicUser = Omit<User, 'password' | 'email'>;

// Make all properties optional (for updates)
type UserUpdate = Partial<User>;

// Make all properties required
type CompleteUser = Required<User>;

// Extract function return type
type ApiResponse = ReturnType<typeof fetchUser>;

// Extract promise resolved type
type UserData = Awaited<ReturnType<typeof fetchUser>>;
```

### 4. Generic Constraints

```typescript
// BAD - Overly generic
function getProperty<T>(obj: T, key: string): any {
  return obj[key];
}

// GOOD - Constrained generic with proper return type
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Usage
const user = { name: 'John', age: 30 };
const name = getProperty(user, 'name'); // type: string
const age = getProperty(user, 'age');   // type: number
```

## -Specific Patterns

### API Response Types (api)

```typescript
// Standard API response wrapper
interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta?: {
    page: number;
    limit: number;
    total: number;
  };
}

// Error response
interface ApiError {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}

type ApiResult<T> = ApiResponse<T> | ApiError;
```

### Redux State Types (mobile-app)

```typescript
// Typed selector with reselect
import { createSelector } from 'reselect';

const selectUsers = (state: RootState) => state.users.items;
const selectFilter = (state: RootState) => state.users.filter;

export const selectFilteredUsers = createSelector(
  [selectUsers, selectFilter],
  (users, filter) => users.filter(u => u.status === filter)
);
```

### Redux Toolkit Types (web-app)

```typescript
// Typed slice with createSlice
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UsersState {
  items: User[];
  loading: boolean;
  error: string | null;
}

const usersSlice = createSlice({
  name: 'users',
  initialState: { items: [], loading: false, error: null } as UsersState,
  reducers: {
    setUsers: (state, action: PayloadAction<User[]>) => {
      state.items = action.payload;
    },
  },
});
```

## Zod Integration (api)

```typescript
import { z } from 'zod';

// Define schema
const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(100),
  email: z.string().email(),
  role: z.enum(['admin', 'user', 'guest']),
});

// Infer TypeScript type from schema
type User = z.infer<typeof UserSchema>;

// Validate with proper error handling
function validateUser(data: unknown): User {
  return UserSchema.parse(data); // Throws ZodError if invalid
}

// Safe validation
function safeValidateUser(data: unknown): User | null {
  const result = UserSchema.safeParse(data);
  return result.success ? result.data : null;
}
```

## Strict Mode Checklist

Enable these in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  }
}
```
