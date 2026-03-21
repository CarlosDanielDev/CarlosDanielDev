# Redux Pattern (mobile-app)

This pattern is based on the Redux implementation used in `mobile-app/src/stores/variants/`.

## Overview

The mobile-app uses **traditional Redux with TypeScript** (NOT Redux Toolkit hooks). Key characteristics:
- Action type constants
- Typed action interfaces
- Reducer with switch statements
- Async actions with redux-thunk
- `connect()` HOC (NOT useSelector/useDispatch hooks)

## Directory Structure

```
src/stores/{domain}/
├── {domain}.types.ts          # State interface, action type constants, action interfaces
├── {domain}.reducer.ts        # Reducer with switch statement
├── actions/
│   ├── {domain}.actions.ts         # Sync action creators
│   └── {domain}.async.actions.ts   # Async action creators (thunks)
└── reducers/
    └── {sub-domain}.reducer.ts     # Sub-reducers if needed
```

## Types File Pattern (`{domain}.types.ts`)

```typescript
import { Action } from 'redux'

// 1. Domain interfaces
export interface IMyItem {
  id: string
  name: string
  active?: boolean
}

// 2. Action type constants (string literals)
export const SET_ITEMS = 'SET_ITEMS'
export const ADD_ITEM = 'ADD_ITEM'
export const UPDATE_ITEM = 'UPDATE_ITEM'
export const DELETE_ITEM = 'DELETE_ITEM'
export const SET_LOADING = 'SET_LOADING'
export const SET_SELECTED = 'SET_SELECTED'
export const RESET_STATE = 'RESET_STATE'

// 3. Action interfaces (one per action type)
export interface ISetItemsAction extends Action {
  type: typeof SET_ITEMS
  payload: IMyItem[]
}

export interface IAddItemAction extends Action {
  type: typeof ADD_ITEM
  payload: IMyItem
}

export interface IUpdateItemAction extends Action {
  type: typeof UPDATE_ITEM
  payload: IMyItem
}

export interface IDeleteItemAction extends Action {
  type: typeof DELETE_ITEM
  payload: string // item id
}

export interface ISetLoadingAction extends Action {
  type: typeof SET_LOADING
  payload: boolean
}

export interface ISetSelectedAction extends Action {
  type: typeof SET_SELECTED
  payload: IMyItem | undefined
}

export interface IResetStateAction extends Action {
  type: typeof RESET_STATE
  payload: void
}

// 4. Union type for all actions
export type MyDomainActionTypes =
  | ISetItemsAction
  | IAddItemAction
  | IUpdateItemAction
  | IDeleteItemAction
  | ISetLoadingAction
  | ISetSelectedAction
  | IResetStateAction

// 5. State interface
export interface IMyDomainState {
  list: IMyItem[]
  selected?: IMyItem
  isLoading: boolean
  notifications: any[]
}
```

## Reducer Pattern (`{domain}.reducer.ts`)

```typescript
import {
  IMyDomainState,
  MyDomainActionTypes,
  SET_ITEMS,
  ADD_ITEM,
  UPDATE_ITEM,
  DELETE_ITEM,
  SET_LOADING,
  SET_SELECTED,
  RESET_STATE,
} from './{domain}.types'
import { LOGOUT } from '../actions/types'

const initialState: IMyDomainState = {
  list: [],
  selected: undefined,
  isLoading: false,
  notifications: [],
}

const MyDomainReducer = (
  state: IMyDomainState = initialState,
  action: MyDomainActionTypes
): IMyDomainState => {
  switch (action.type) {
    case SET_ITEMS:
      return {
        ...state,
        list: action.payload,
      }

    case ADD_ITEM:
      return {
        ...state,
        list: [...state.list, action.payload],
      }

    case UPDATE_ITEM: {
      const updatedList = state.list.map((item) =>
        item.id === action.payload.id ? action.payload : item
      )
      return {
        ...state,
        list: updatedList,
      }
    }

    case DELETE_ITEM:
      return {
        ...state,
        list: state.list.filter((item) => item.id !== action.payload),
      }

    case SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      }

    case SET_SELECTED:
      return {
        ...state,
        selected: action.payload,
      }

    case RESET_STATE:
      return { ...initialState }

    case LOGOUT:
      return initialState

    default:
      return state
  }
}

export default MyDomainReducer
```

## Sync Actions Pattern (`actions/{domain}.actions.ts`)

```typescript
import {
  SET_ITEMS,
  ADD_ITEM,
  UPDATE_ITEM,
  DELETE_ITEM,
  SET_LOADING,
  SET_SELECTED,
  RESET_STATE,
  IMyItem,
} from '../{domain}.types'

// Action creators return plain objects
export const setItems = (items: IMyItem[]) => ({
  type: SET_ITEMS,
  payload: items,
})

export const addItem = (item: IMyItem) => ({
  type: ADD_ITEM,
  payload: item,
})

export const updateItem = (item: IMyItem) => ({
  type: UPDATE_ITEM,
  payload: item,
})

export const deleteItem = (itemId: string) => ({
  type: DELETE_ITEM,
  payload: itemId,
})

export const setLoading = (isLoading: boolean) => ({
  type: SET_LOADING,
  payload: isLoading,
})

export const setSelected = (item: IMyItem | undefined) => ({
  type: SET_SELECTED,
  payload: item,
})

export const resetState = () => ({
  type: RESET_STATE,
})
```

## Async Actions Pattern (`actions/{domain}.async.actions.ts`)

```typescript
import { Dispatch } from 'redux'
import { setItems, setLoading, addItem } from './{domain}.actions'
import { IMyItem } from '../{domain}.types'
import { apiClient } from '../../api/client'

// Async action using redux-thunk
export const fetchItems = (params: { aid: string }) => {
  return async (dispatch: Dispatch) => {
    try {
      dispatch(setLoading(true))

      const response = await apiClient.get('/items', { params })

      dispatch(setItems(response.data))

      return response.data
    } catch (error) {
      console.error('Failed to fetch items:', error)
      throw error
    } finally {
      dispatch(setLoading(false))
    }
  }
}

export const createItem = (
  item: Partial<IMyItem>,
  callback?: (error?: Error) => void
) => {
  return async (dispatch: Dispatch) => {
    try {
      dispatch(setLoading(true))

      const response = await apiClient.post('/items', item)

      dispatch(addItem(response.data))

      callback?.()
      return response.data
    } catch (error) {
      console.error('Failed to create item:', error)
      callback?.(error as Error)
      throw error
    } finally {
      dispatch(setLoading(false))
    }
  }
}
```

## Component Connection Pattern

**IMPORTANT:** Use `connect()` HOC, NOT hooks (useSelector/useDispatch).

```typescript
import React from 'react'
import { connect } from 'react-redux'
import { fetchItems, createItem } from '../../stores/{domain}/actions/{domain}.async.actions'
import { setSelected } from '../../stores/{domain}/actions/{domain}.actions'

interface Props {
  // From mapStateToProps
  items: IMyItem[]
  isLoading: boolean
  selected?: IMyItem
  // From mapDispatchToProps
  fetchItems: typeof fetchItems
  createItem: typeof createItem
  setSelected: typeof setSelected
  // Own props
  navigation: any
}

const MyScreen = ({ items, isLoading, fetchItems, createItem, setSelected }: Props) => {
  // Component implementation
  return (
    // JSX
  )
}

// Connect to Redux store
export default connect(
  // mapStateToProps - select state slices
  ({ myDomain, auth }: RootState) => ({
    items: myDomain.list,
    isLoading: myDomain.isLoading,
    selected: myDomain.selected,
    uid: auth.user.uid,
  }),
  // mapDispatchToProps - action creators
  {
    fetchItems,
    createItem,
    setSelected,
  }
)(MyScreen)
```

## Sub-Reducer Pattern

When state gets complex, extract sub-reducers:

```typescript
// reducers/{sub-domain}.reducer.ts
export interface SubDomainState {
  mode: 'create' | 'edit'
  isLoading: boolean
  data: any
}

const initialSubState: SubDomainState = {
  mode: 'create',
  isLoading: false,
  data: null,
}

export const subDomainReducer = (
  state: SubDomainState = initialSubState,
  action: SubDomainActionTypes
): SubDomainState => {
  switch (action.type) {
    case SET_SUB_MODE:
      return { ...state, mode: action.payload }
    // ... other cases
    default:
      return state
  }
}

// In main reducer, delegate to sub-reducer:
default:
  const newSubState = subDomainReducer(state.subDomain, action as SubDomainActionTypes)
  if (newSubState !== state.subDomain) {
    return { ...state, subDomain: newSubState }
  }
  return state
```

## Key Rules

1. **Always use `connect()`** - Never use `useSelector`/`useDispatch` hooks
2. **Type everything** - All actions, state, and props should be typed
3. **Action constants** - Use string literal constants exported as `const`
4. **Immutable updates** - Always spread state, never mutate
5. **Callback pattern** - Async actions can accept callbacks for component-level error handling
6. **Logout handling** - Always reset to `initialState` on LOGOUT action
