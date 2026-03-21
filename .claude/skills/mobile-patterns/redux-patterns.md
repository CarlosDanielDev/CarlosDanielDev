# Redux Patterns for mobile-app

Complete Redux patterns using `connect()` (NOT hooks).

## Redux Structure

```
src/stores/
├── actions/
│   ├── {Feature}Actions.js
│   ├── types.js
│   └── index.js
├── reducers/
│   ├── {Feature}Reducer.js
│   └── index.js
├── variants/
└── _business/
```

---

## Action Pattern

### Standard Action with Async

```javascript
// stores/actions/ProductActions.js
import { PRODUCTS_FETCH, PRODUCTS_FETCH_ERROR, START_LOADING, STOP_LOADING } from './types'
import { fetch } from '../../repository'
import { PRODUCT } from '../../repository/endpoints'

export function productsFetch(params) {
  return async (dispatch, getState) => {
    try {
      dispatch({ type: START_LOADING })

      // Get user aid from state
      const aid = getState()?.auth?.user.aid ?? ''

      // Fetch data
      const response = await fetch(PRODUCT, params, aid)

      // Dispatch success
      dispatch({
        type: PRODUCTS_FETCH,
        payload: response.data
      })
    } catch (error) {
      // Dispatch error
      dispatch({
        type: PRODUCTS_FETCH_ERROR,
        payload: error.message
      })
    } finally {
      dispatch({ type: STOP_LOADING })
    }
  }
}
```

### Action with Parameters

```javascript
export function productSave(product) {
  return async (dispatch, getState) => {
    try {
      dispatch(startLoading())

      const aid = getState()?.auth?.user.aid ?? ''
      const response = await save(PRODUCT, product, aid)

      dispatch({
        type: PRODUCT_SAVE_SUCCESS,
        payload: response.data
      })

      return response.data
    } catch (error) {
      dispatch({
        type: PRODUCT_SAVE_ERROR,
        payload: error
      })
      throw error
    } finally {
      dispatch(stopLoading())
    }
  }
}
```

### Action Types

```javascript
// stores/actions/types.js
export const PRODUCTS_FETCH = 'PRODUCTS_FETCH'
export const PRODUCTS_FETCH_ERROR = 'PRODUCTS_FETCH_ERROR'
export const PRODUCT_SAVE = 'PRODUCT_SAVE'
export const PRODUCT_SAVE_SUCCESS = 'PRODUCT_SAVE_SUCCESS'
export const PRODUCT_SAVE_ERROR = 'PRODUCT_SAVE_ERROR'
export const START_LOADING = 'START_LOADING'
export const STOP_LOADING = 'STOP_LOADING'
```

---

## Reducer Pattern

```javascript
// stores/reducers/ProductReducer.js
import {
  PRODUCTS_FETCH,
  PRODUCTS_FETCH_ERROR,
  PRODUCT_SAVE_SUCCESS,
} from '../actions/types'

const INITIAL_STATE = {
  list: [],
  selected: null,
  loading: false,
  error: null,
}

export default (state = INITIAL_STATE, action) => {
  switch (action.type) {
    case PRODUCTS_FETCH:
      return {
        ...state,
        list: action.payload,
        error: null,
      }

    case PRODUCTS_FETCH_ERROR:
      return {
        ...state,
        error: action.payload,
      }

    case PRODUCT_SAVE_SUCCESS:
      return {
        ...state,
        list: [...state.list, action.payload],
        selected: action.payload,
      }

    default:
      return state
  }
}
```

### Root Reducer

```javascript
// stores/reducers/index.js
import { combineReducers } from 'redux'
import { reducer as formReducer } from 'redux-form'
import AuthReducer from './AuthReducer'
import ProductReducer from './ProductReducer'

export default combineReducers({
  form: formReducer,
  auth: AuthReducer,
  products: ProductReducer,
})
```

---

## Component Connection

### Basic Connection

```typescript
import { connect } from 'react-redux'
import { RootState } from '../types/state/RootState'

type StateProps = ReturnType<typeof mapStateToProps>

const MyComponent: React.FC<StateProps> = ({ user, products }) => {
  return <View>{/* Component JSX */}</View>
}

const mapStateToProps = (state: RootState) => ({
  user: state.auth.user,
  products: state.products.list,
})

export default connect(mapStateToProps)(MyComponent)
```

### With Actions

```typescript
import { connect } from 'react-redux'
import { someAction, anotherAction } from '../stores/actions'
import { RootState } from '../types/state/RootState'

type StateProps = ReturnType<typeof mapStateToProps>

type ActionProps = {
  someAction: typeof someAction
  anotherAction: typeof anotherAction
}

type Props = StateProps & ActionProps

const MyComponent: React.FC<Props> = ({
  user,
  products,
  someAction,
  anotherAction
}) => {
  useEffect(() => {
    someAction({})
  }, [someAction])

  const handlePress = useCallback(() => {
    anotherAction({ id: 123 })
  }, [anotherAction])

  return <View>{/* Component JSX */}</View>
}

const mapStateToProps = (state: RootState) => ({
  user: state.auth.user,
  products: state.products.list,
})

const mapDispatchToProps = {
  someAction,
  anotherAction,
}

export default connect(mapStateToProps, mapDispatchToProps)(MyComponent)
```

### With Own Props (from navigation/parent)

```typescript
import { NavigationProp } from '@react-navigation/native'

type StateProps = ReturnType<typeof mapStateToProps>
type ActionProps = typeof mapDispatchToProps

type OwnProps = {
  navigation: NavigationProp<any>
  route: any
}

type Props = StateProps & ActionProps & OwnProps

const MyComponent: React.FC<Props> = ({
  navigation,
  route,
  user,
  someAction
}) => {
  // Access route params
  const { productId } = route.params || {}

  useEffect(() => {
    someAction({ productId })
  }, [productId, someAction])

  return <View>{/* Component JSX */}</View>
}

const mapStateToProps = (state: RootState) => ({
  user: state.auth.user,
})

const mapDispatchToProps = {
  someAction,
}

export default connect(mapStateToProps, mapDispatchToProps)(MyComponent)
```

---

## Selectors (Optional Optimization)

```typescript
// stores/selectors/productSelectors.ts
import { RootState } from '../types/state/RootState'

export const selectProducts = (state: RootState) => state.products.list

export const selectActiveProducts = (state: RootState) =>
  state.products.list.filter(p => p.status === 'active')

export const selectProductById = (state: RootState, id: string) =>
  state.products.list.find(p => p.id === id)

// Usage in component
const mapStateToProps = (state: RootState, ownProps: OwnProps) => ({
  product: selectProductById(state, ownProps.route.params.id),
  activeProducts: selectActiveProducts(state),
})
```

---

## redux-form Integration

### Form Component

```typescript
import { Field, reduxForm, InjectedFormProps } from 'redux-form'
import FieldInput from 'components/common/form/FieldInput'
import { generateTestID } from '../../util'

type FormData = {
  name: string
  email: string
  phone: string
}

type Props = InjectedFormProps<FormData>

const ProductForm: React.FC<Props> = ({ handleSubmit }) => (
  <View>
    <Field
      name="name"
      component={FieldInput}
      placeholder="Product Name"
      testProps={generateTestID('product-name-input')}
    />
    <Field
      name="price"
      component={FieldInput}
      placeholder="Price"
      keyboardType="numeric"
      testProps={generateTestID('product-price-input')}
    />
    <Button {...generateTestID('save-button')} onPress={handleSubmit}>
      Save
    </Button>
  </View>
)

export default reduxForm<FormData>({
  form: 'productForm'
})(ProductForm)
```

### Form with Validation

```typescript
const validate = (values: FormData) => {
  const errors: Partial<FormData> = {}

  if (!values.name) {
    errors.name = 'Name is required'
  }

  if (!values.price || parseFloat(values.price) <= 0) {
    errors.price = 'Valid price is required'
  }

  return errors
}

export default reduxForm<FormData>({
  form: 'productForm',
  validate,
})(ProductForm)
```

### Submitting Form in Screen

```typescript
import { connect } from 'react-redux'
import { submit } from 'redux-form'
import { productSave } from '../stores/actions'

const ProductScreen: React.FC<Props> = ({
  navigation,
  submitForm,
  productSave
}) => {
  const handleSave = async (values: FormData) => {
    try {
      await productSave(values)
      navigation.goBack()
    } catch (error) {
      Alert.alert('Error', 'Failed to save product')
    }
  }

  return (
    <Screen
      navigation={navigation}
      title="Add Product"
      rightButtons={[
        {
          icon: 'save',
          onPress: () => submitForm('productForm')
        }
      ]}
    >
      <ProductForm onSubmit={handleSave} />
    </Screen>
  )
}

const mapDispatchToProps = {
  submitForm: () => submit('productForm'),
  productSave,
}

export default connect(null, mapDispatchToProps)(ProductScreen)
```

---

## Why connect() Instead of Hooks?

**mobile-app uses `connect()` for consistency and performance:**

1. ✅ **Explicit dependencies** - clear what component needs
2. ✅ **Optimized re-renders** - built-in shallow comparison
3. ✅ **Established pattern** - entire codebase uses it
4. ✅ **Better testability** - mock mapStateToProps/mapDispatchToProps

❌ **DO NOT introduce hooks** - creates pattern inconsistency
