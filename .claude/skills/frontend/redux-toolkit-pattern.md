# Redux Toolkit Pattern (web-app / admin-panel)

This pattern is based on the Redux Toolkit implementation used in `web-app` and `control` repositories.

## Overview

Redux Toolkit (RTK) is the modern, official Redux approach. Key characteristics:
- `createSlice` for reducers and actions
- `createAsyncThunk` for async operations
- `createSelector` for memoized selectors
- `useAppSelector` / `useAppDispatch` hooks (NOT connect())
- Built-in Immer for immutable updates
- Full TypeScript support

## Package Versions

```json
{
  "@reduxjs/toolkit": "^2.0.1",
  "react-redux": "^9.0.0"
}
```

## Directory Structure

```
src/store/
├── index.ts                    # Store configuration & type exports
├── hooks.ts                    # Typed useAppSelector & useAppDispatch
├── slices/
│   └── {domain}/
│       ├── {domain}.slice.ts       # Slice definition
│       ├── {domain}.types.ts       # TypeScript interfaces
│       ├── {domain}.selectors.ts   # Memoized selectors (optional)
│       ├── actions/
│       │   └── {action}.action.ts  # Synchronous actions (extracted)
│       ├── thunks/
│       │   └── {thunk}.thunk.ts    # Async thunks
│       └── cases/
│           └── {thunk}.case.ts     # extraReducers case builders
```

## Store Configuration (`index.ts`)

```typescript
import { configureStore, Action, ThunkAction } from '@reduxjs/toolkit'

import authReducer from './slices/auth/auth.slice'
import productsReducer from './slices/products/products.slice'
import salesReducer from './slices/sales/sales.slice'

const isDevelopment = (): boolean => __DEV__ || process.env.NODE_ENV === 'development'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    products: productsReducer,
    sales: salesReducer,
  },
  devTools: isDevelopment(),
})

// Type exports
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>
```

### With Redux Persist (React Native)

```typescript
import { configureStore, Action } from '@reduxjs/toolkit'
import { persistReducer, persistStore, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from 'redux-persist'
import AsyncStorage from '@react-native-async-storage/async-storage'

const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth'],
}

const persistedAuthReducer = persistReducer(persistConfig, authReducer)

export const store = configureStore({
  reducer: {
    auth: persistedAuthReducer,
    // ... other reducers
  },
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
})

export const persistor = persistStore(store)
```

## Typed Hooks (`hooks.ts`)

```typescript
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux'
import type { RootState, AppDispatch } from '.'

export const useAppDispatch = (): AppDispatch => useDispatch<AppDispatch>()
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector
```

## Types File (`{domain}.types.ts`)

```typescript
export interface IProduct {
  id: string
  name: string
  price: number
  stock: number
  categoryId?: string
  active: boolean
}

export interface IProductFilters {
  search: string
  categoryId: string | null
  skip: number
  limit: number
}

export interface IProductsState {
  list: IProduct[]
  loading: boolean
  error: string | null
  filter: IProductFilters
  total: number
}
```

## Slice Pattern (`{domain}.slice.ts`)

```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { IProductsState, IProduct } from './products.types'

// Import extracted actions
import { setSearchTermAction } from './actions/set-search-term.action'

// Import case builders
import { addFetchProductsCase } from './cases/fetch-products.case'
import { addSaveProductCase } from './cases/save-product.case'

const initialState: IProductsState = {
  list: [],
  loading: false,
  error: null,
  filter: {
    search: '',
    categoryId: null,
    skip: 0,
    limit: 20,
  },
  total: 0,
}

const productsSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    // Extracted action
    setSearchTerm: setSearchTermAction,

    // Inline reducers
    resetProducts: state => {
      state.list = []
      state.filter.skip = 0
    },

    updateProduct: (state, action: PayloadAction<IProduct>) => {
      const index = state.list.findIndex(p => p.id === action.payload.id)
      if (index !== -1) {
        state.list[index] = action.payload
      }
    },

    clearError: state => {
      state.error = null
    },
  },
  extraReducers: builder => {
    addFetchProductsCase(builder)
    addSaveProductCase(builder)
  },
})

export const { setSearchTerm, resetProducts, updateProduct, clearError } = productsSlice.actions
export default productsSlice.reducer
```

## Extracted Action (`actions/{action}.action.ts`)

```typescript
import { PayloadAction } from '@reduxjs/toolkit'
import { IProductsState } from '../products.types'

export const setSearchTermAction = (
  state: IProductsState,
  action: PayloadAction<string>
): void => {
  state.filter.search = action.payload
  state.filter.skip = 0
}
```

## Async Thunk (`thunks/{thunk}.thunk.ts`)

### Basic Thunk

```typescript
import { createAsyncThunk } from '@reduxjs/toolkit'
import { RootState } from '@/store'
import { apiGetProducts } from '@/services/api-client'

interface FetchProductsPayload {
  reset?: boolean
}

interface FetchProductsResult {
  list: IProduct[]
  total: number
  skip: number
}

export const fetchProducts = createAsyncThunk<
  FetchProductsResult,      // Return type
  FetchProductsPayload,     // Argument type
  { state: RootState }      // ThunkAPI config
>(
  'products/fetchProducts',
  async ({ reset }, { getState }) => {
    const { auth, products } = getState()
    const aid = auth.user?.aid || ''

    const filters = {
      ...products.filter,
      skip: reset ? 0 : products.filter.skip,
    }

    const response = await apiGetProducts(aid, filters)

    return {
      list: response.data._products,
      total: response.data.count,
      skip: filters.skip,
    }
  }
)
```

### Thunk with Error Handling

```typescript
import { createAsyncThunk } from '@reduxjs/toolkit'
import { addNotification } from '@/store/slices/common/common.slice'

export const saveProduct = createAsyncThunk<
  IProduct,
  Partial<IProduct>,
  { state: RootState; rejectValue: string }
>(
  'products/saveProduct',
  async (productData, { getState, dispatch, rejectWithValue }) => {
    try {
      const { auth } = getState()
      const isUpdate = Boolean(productData.id)

      const response = await apiSaveProduct(
        auth.user?.aid || '',
        productData,
        isUpdate ? 'put' : 'post'
      )

      dispatch(addNotification({
        type: 'success',
        message: isUpdate ? 'Product updated!' : 'Product created!',
      }))

      return response.data
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        message: 'Failed to save product',
      }))

      return rejectWithValue(error.message || 'Unknown error')
    }
  }
)
```

## Case Builder (`cases/{thunk}.case.ts`)

```typescript
import { ActionReducerMapBuilder, PayloadAction } from '@reduxjs/toolkit'
import { IProductsState } from '../products.types'
import { fetchProducts } from '../thunks/fetch-products.thunk'

export const addFetchProductsCase = (
  builder: ActionReducerMapBuilder<IProductsState>
): void => {
  builder
    .addCase(fetchProducts.pending, state => {
      state.loading = true
      state.error = null
    })
    .addCase(fetchProducts.fulfilled, (state, action) => {
      const { list, total, skip } = action.payload

      state.list = skip > 0 ? [...state.list, ...list] : list
      state.total = total
      state.filter.skip = skip + list.length
      state.loading = false
    })
    .addCase(fetchProducts.rejected, (state, action) => {
      state.loading = false
      state.error = action.error.message || 'Failed to fetch'
    })
}
```

## Selectors (`{domain}.selectors.ts`)

```typescript
import { createSelector } from '@reduxjs/toolkit'
import { RootState } from '@/store'

// Input selectors
const selectProductsState = (state: RootState) => state.products

// Simple selectors
export const selectProducts = (state: RootState) => state.products.list
export const selectProductsLoading = (state: RootState) => state.products.loading

// Memoized selector
export const selectFilteredProducts = createSelector(
  [selectProductsState],
  products => {
    const { list, filter } = products

    if (!filter.search) return list

    const searchLower = filter.search.toLowerCase()
    return list.filter(product =>
      product.name.toLowerCase().includes(searchLower)
    )
  }
)

// Selector factory
export const selectProductById = (productId: string) =>
  createSelector([selectProducts], products =>
    products.find(p => p.id === productId)
  )
```

## Component Integration

**IMPORTANT:** Use hooks, NOT `connect()`.

```typescript
import React, { useEffect, useCallback } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { fetchProducts } from '@/store/slices/products/thunks/fetch-products.thunk'
import { setSearchTerm, resetProducts } from '@/store/slices/products/products.slice'
import { selectFilteredProducts, selectProductsLoading } from '@/store/slices/products/products.selectors'

export function ProductList() {
  const dispatch = useAppDispatch()

  // Use selectors
  const products = useAppSelector(selectFilteredProducts)
  const loading = useAppSelector(selectProductsLoading)

  // Fetch on mount
  useEffect(() => {
    dispatch(fetchProducts({ reset: true }))

    return () => {
      dispatch(resetProducts())
    }
  }, [dispatch])

  // Handlers
  const handleSearch = useCallback((text: string) => {
    dispatch(setSearchTerm(text))
  }, [dispatch])

  const handleLoadMore = useCallback(() => {
    if (!loading) {
      dispatch(fetchProducts({ reset: false }))
    }
  }, [dispatch, loading])

  return (
    <FlatList
      data={products}
      renderItem={({ item }) => <ProductItem product={item} />}
      keyExtractor={item => item.id}
      onEndReached={handleLoadMore}
    />
  )
}
```

## Custom Hook Pattern

```typescript
// hooks/useProducts.ts
import { useCallback } from 'react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { fetchProducts } from '@/store/slices/products/thunks/fetch-products.thunk'
import { selectFilteredProducts, selectProductsLoading } from '@/store/slices/products/products.selectors'

export function useProducts() {
  const dispatch = useAppDispatch()

  const products = useAppSelector(selectFilteredProducts)
  const loading = useAppSelector(selectProductsLoading)
  const error = useAppSelector(state => state.products.error)

  const fetch = useCallback((reset = false) => {
    return dispatch(fetchProducts({ reset }))
  }, [dispatch])

  return { products, loading, error, fetch }
}
```

## Key Rules

1. **Always use hooks** - Use `useAppSelector`/`useAppDispatch`, NOT `connect()`
2. **Type everything** - Fully type thunks with generics: `createAsyncThunk<Return, Arg, Config>`
3. **Extract case builders** - Keep slices clean by extracting async handlers
4. **Use createSelector** - Memoize computed state to prevent re-renders
5. **Immer mutations** - Write "mutating" code in reducers (Immer handles immutability)
6. **Dispatch in deps** - Always include `dispatch` in useEffect/useCallback dependency arrays

## Migration from connect() to Hooks

### Before (connect)

```typescript
const MyComponent = ({ items, fetchItems }) => { ... }

export default connect(
  state => ({ items: state.products.list }),
  { fetchItems }
)(MyComponent)
```

### After (hooks)

```typescript
function MyComponent() {
  const dispatch = useAppDispatch()
  const items = useAppSelector(state => state.products.list)

  useEffect(() => {
    dispatch(fetchItems())
  }, [dispatch])

  return ...
}
```
