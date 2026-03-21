# State Management - web-app

## Redux Toolkit Patterns

### 1. Slice Structure

```typescript
// features/users/users.slice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UsersState {
  items: User[];
  selectedId: string | null;
  loading: boolean;
  error: string | null;
}

const initialState: UsersState = {
  items: [],
  selectedId: null,
  loading: false,
  error: null,
};

const usersSlice = createSlice({
  name: 'users',
  initialState,
  reducers: {
    setUsers: (state, action: PayloadAction<User[]>) => {
      state.items = action.payload;
    },
    selectUser: (state, action: PayloadAction<string>) => {
      state.selectedId = action.payload;
    },
    clearSelection: (state) => {
      state.selectedId = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? 'Failed to fetch users';
      });
  },
});

export const { setUsers, selectUser, clearSelection } = usersSlice.actions;
export default usersSlice.reducer;
```

### 2. Async Thunks

```typescript
// features/users/users.thunks.ts
import { createAsyncThunk } from '@reduxjs/toolkit';

export const fetchUsers = createAsyncThunk(
  'users/fetchUsers',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/users');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateUser = createAsyncThunk(
  'users/updateUser',
  async (userData: UserUpdate, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/users/${userData.id}`, userData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);
```

### 3. Selectors with Memoization

```typescript
// features/users/users.selectors.ts
import { createSelector } from '@reduxjs/toolkit';
import type { RootState } from '../../store';

// Basic selectors
export const selectUsers = (state: RootState) => state.users.items;
export const selectUsersLoading = (state: RootState) => state.users.loading;
export const selectSelectedUserId = (state: RootState) => state.users.selectedId;

// Memoized selectors
export const selectActiveUsers = createSelector(
  [selectUsers],
  (users) => users.filter(u => u.isActive)
);

export const selectSelectedUser = createSelector(
  [selectUsers, selectSelectedUserId],
  (users, selectedId) => users.find(u => u.id === selectedId) ?? null
);

export const selectUsersByRole = createSelector(
  [selectUsers, (_, role: string) => role],
  (users, role) => users.filter(u => u.role === role)
);
```

## RTK Query for API Caching

### 1. API Slice Setup

```typescript
// services/api.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api',
    prepareHeaders: (headers, { getState }) => {
      const token = (getState() as RootState).auth.token;
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['User', 'Product', 'Order'],
  endpoints: () => ({}),
});
```

### 2. Inject Endpoints

```typescript
// services/users.api.ts
import { api } from './api';

export const usersApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getUsers: builder.query<User[], void>({
      query: () => '/users',
      providesTags: (result) =>
        result
          ? [...result.map(({ id }) => ({ type: 'User' as const, id })), 'User']
          : ['User'],
    }),

    getUser: builder.query<User, string>({
      query: (id) => `/users/${id}`,
      providesTags: (_, __, id) => [{ type: 'User', id }],
    }),

    updateUser: builder.mutation<User, Partial<User> & Pick<User, 'id'>>({
      query: ({ id, ...patch }) => ({
        url: `/users/${id}`,
        method: 'PATCH',
        body: patch,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'User', id }],
    }),

    deleteUser: builder.mutation<void, string>({
      query: (id) => ({
        url: `/users/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (_, __, id) => [{ type: 'User', id }],
    }),
  }),
});

export const {
  useGetUsersQuery,
  useGetUserQuery,
  useUpdateUserMutation,
  useDeleteUserMutation,
} = usersApi;
```

### 3. Optimistic Updates

```typescript
updateUser: builder.mutation<User, Partial<User> & Pick<User, 'id'>>({
  query: ({ id, ...patch }) => ({
    url: `/users/${id}`,
    method: 'PATCH',
    body: patch,
  }),
  async onQueryStarted({ id, ...patch }, { dispatch, queryFulfilled }) {
    // Optimistic update
    const patchResult = dispatch(
      usersApi.util.updateQueryData('getUsers', undefined, (draft) => {
        const user = draft.find(u => u.id === id);
        if (user) {
          Object.assign(user, patch);
        }
      })
    );

    try {
      await queryFulfilled;
    } catch {
      // Rollback on error
      patchResult.undo();
    }
  },
}),
```

### 4. Polling and Refetching

```tsx
function LiveDashboard() {
  // Poll every 30 seconds
  const { data: stats } = useGetDashboardStatsQuery(undefined, {
    pollingInterval: 30000,
  });

  // Refetch on window focus
  const { data: notifications } = useGetNotificationsQuery(undefined, {
    refetchOnFocus: true,
    refetchOnReconnect: true,
  });

  return <Dashboard stats={stats} notifications={notifications} />;
}
```

## react-hook-form Patterns

### 1. Basic Form

```tsx
import { useForm, SubmitHandler } from 'react-hook-form';

interface FormData {
  email: string;
  password: string;
}

function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>();

  const onSubmit: SubmitHandler<FormData> = async (data) => {
    await login(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('email', {
          required: 'Email is required',
          pattern: {
            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
            message: 'Invalid email address',
          },
        })}
      />
      {errors.email && <span>{errors.email.message}</span>}

      <input
        type="password"
        {...register('password', {
          required: 'Password is required',
          minLength: { value: 8, message: 'Minimum 8 characters' },
        })}
      />
      {errors.password && <span>{errors.password.message}</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Loading...' : 'Login'}
      </button>
    </form>
  );
}
```

### 2. Controlled Fields (ui-components)

```tsx
import { Controller } from 'react-hook-form';
import { Select, DatePicker } from '@company/ui-components/web';

function ProductForm() {
  const { control, handleSubmit } = useForm<ProductFormData>();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="category"
        control={control}
        rules={{ required: 'Category is required' }}
        render={({ field, fieldState }) => (
          <Select
            {...field}
            options={categoryOptions}
            error={fieldState.error?.message}
          />
        )}
      />

      <Controller
        name="releaseDate"
        control={control}
        render={({ field }) => (
          <DatePicker
            value={field.value}
            onChange={field.onChange}
          />
        )}
      />
    </form>
  );
}
```

### 3. Form with Zod Validation

```tsx
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const productSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  price: z.number().positive('Price must be positive'),
  category: z.enum(['electronics', 'clothing', 'food']),
  description: z.string().optional(),
});

type ProductFormData = z.infer<typeof productSchema>;

function ProductForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('name')} />
      <input type="number" {...register('price', { valueAsNumber: true })} />
      <select {...register('category')}>
        <option value="electronics">Electronics</option>
        <option value="clothing">Clothing</option>
        <option value="food">Food</option>
      </select>
    </form>
  );
}
```

### 4. Field Array (Dynamic Fields)

```tsx
import { useFieldArray } from 'react-hook-form';

function OrderForm() {
  const { control, register } = useForm<OrderFormData>();
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  return (
    <form>
      {fields.map((field, index) => (
        <div key={field.id}>
          <input {...register(`items.${index}.productId`)} />
          <input
            type="number"
            {...register(`items.${index}.quantity`, { valueAsNumber: true })}
          />
          <button type="button" onClick={() => remove(index)}>
            Remove
          </button>
        </div>
      ))}

      <button type="button" onClick={() => append({ productId: '', quantity: 1 })}>
        Add Item
      </button>
    </form>
  );
}
```

## Avoid Prop Drilling

### 1. Context for Theme/Config

```tsx
// contexts/ThemeContext.tsx
const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>('light');

  const value = useMemo(
    () => ({ theme, setTheme }),
    [theme]
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

### 2. Composition Over Context

```tsx
// Instead of context for everything, use composition
// BAD - Props drilling
<Page>
  <Header user={user} onLogout={onLogout}>
    <Navigation user={user}>
      <UserMenu user={user} onLogout={onLogout} />
    </Navigation>
  </Header>
</Page>

// GOOD - Composition
<Page>
  <Header
    userMenu={<UserMenu user={user} onLogout={onLogout} />}
  />
</Page>
```

### 3. Redux for Shared State

```tsx
// Use Redux when state is:
// - Shared across many components
// - Modified by multiple components
// - Needs to persist across routes

// Don't use Redux for:
// - Local UI state (open/closed, hover, etc.)
// - Form state (use react-hook-form)
// - Server cache (use RTK Query)
```
