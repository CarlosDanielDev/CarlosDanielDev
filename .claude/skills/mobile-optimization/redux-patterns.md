# Redux Patterns - mobile-app

## CRITICAL: Use connect(), NOT Hooks

mobile-app uses the traditional Redux pattern with `connect()`. **DO NOT use Redux hooks.**

```tsx
// WRONG - Do NOT use in mobile-app
import { useSelector, useDispatch } from 'react-redux';

// CORRECT - Use connect()
import { connect } from 'react-redux';
```

## connect() Best Practices

### 1. Selective mapStateToProps

```tsx
// BAD - Subscribes to entire store, re-renders on any change
const mapStateToProps = (state: RootState) => ({
  state, // Never do this!
});

// BAD - Creates new object every time
const mapStateToProps = (state: RootState) => ({
  user: { ...state.user }, // New object = always re-render
});

// GOOD - Select only needed primitive values
const mapStateToProps = (state: RootState) => ({
  userId: state.user.id,
  userName: state.user.name,
  isLoading: state.user.loading,
});

// GOOD - Use reselect for derived data
import { createSelector } from 'reselect';

const selectActiveUsers = createSelector(
  (state: RootState) => state.users.items,
  (users) => users.filter(u => u.isActive)
);

const mapStateToProps = (state: RootState) => ({
  activeUsers: selectActiveUsers(state),
});
```

### 2. mapDispatchToProps Optimization

```tsx
// OK - Object shorthand (simple cases)
const mapDispatchToProps = {
  fetchUser,
  updateUser,
  deleteUser,
};

// BETTER - Bound action creators (complex cases)
const mapDispatchToProps = (dispatch: Dispatch) => ({
  fetchUser: (id: string) => dispatch(fetchUser(id)),
  updateUser: (data: UserUpdate) => dispatch(updateUser(data)),
});

// BEST - Use bindActionCreators for many actions
import { bindActionCreators } from 'redux';
import * as userActions from '../actions/userActions';

const mapDispatchToProps = (dispatch: Dispatch) =>
  bindActionCreators(userActions, dispatch);
```

### 3. Complete connect() Example

```tsx
import { connect, ConnectedProps } from 'react-redux';

// Define state selection
const mapStateToProps = (state: RootState) => ({
  user: state.user.data,
  isLoading: state.user.loading,
  error: state.user.error,
});

// Define actions
const mapDispatchToProps = {
  fetchUser,
  updateUser,
};

// Create connector
const connector = connect(mapStateToProps, mapDispatchToProps);

// Infer props type
type PropsFromRedux = ConnectedProps<typeof connector>;

// Component props
interface OwnProps {
  userId: string;
}

type Props = PropsFromRedux & OwnProps;

// Component
class UserProfile extends Component<Props> {
  componentDidMount() {
    this.props.fetchUser(this.props.userId);
  }

  render() {
    const { user, isLoading, error } = this.props;

    if (isLoading) return <Loading />;
    if (error) return <Error message={error} />;
    if (!user) return null;

    return <UserCard user={user} />;
  }
}

export default connector(UserProfile);
```

## Reselect for Memoization

### 1. Basic Selector

```tsx
import { createSelector } from 'reselect';

// Input selectors (simple functions)
const selectUsers = (state: RootState) => state.users.items;
const selectFilter = (state: RootState) => state.users.filter;

// Memoized selector
export const selectFilteredUsers = createSelector(
  [selectUsers, selectFilter],
  (users, filter) => {
    console.log('Computing filtered users...'); // Only logs when inputs change
    return users.filter(u => u.status === filter);
  }
);
```

### 2. Selector with Props

```tsx
// For selectors that need component props
const selectUserId = (_: RootState, props: OwnProps) => props.userId;
const selectUsers = (state: RootState) => state.users.items;

export const selectUserById = createSelector(
  [selectUsers, selectUserId],
  (users, userId) => users.find(u => u.id === userId)
);

// Usage in mapStateToProps
const mapStateToProps = (state: RootState, ownProps: OwnProps) => ({
  user: selectUserById(state, ownProps),
});
```

### 3. Composed Selectors

```tsx
const selectUsers = (state: RootState) => state.users.items;
const selectOrders = (state: RootState) => state.orders.items;

// Selector 1: Active users
const selectActiveUsers = createSelector(
  [selectUsers],
  (users) => users.filter(u => u.isActive)
);

// Selector 2: Compose with orders
const selectActiveUsersWithOrders = createSelector(
  [selectActiveUsers, selectOrders],
  (activeUsers, orders) =>
    activeUsers.map(user => ({
      ...user,
      orders: orders.filter(o => o.userId === user.id),
    }))
);
```

## redux-form Performance

### 1. Field-Level Validation

```tsx
// BAD - Form-level validation runs on every change
const validate = (values: FormValues) => {
  const errors: FormErrors = {};
  if (!values.email) errors.email = 'Required';
  if (!values.password) errors.password = 'Required';
  return errors;
};

// GOOD - Field-level validation runs only for that field
const required = (value: any) => (value ? undefined : 'Required');
const email = (value: string) =>
  value && !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(value)
    ? 'Invalid email'
    : undefined;

<Field name="email" component={Input} validate={[required, email]} />
<Field name="password" component={Input} validate={required} />
```

### 2. Optimize Field Components

```tsx
// Use PureComponent or memo for Field components
class TextInput extends PureComponent<FieldRenderProps> {
  render() {
    const { input, meta, label } = this.props;
    return (
      <View>
        <Text>{label}</Text>
        <TextInput
          {...input}
          onChangeText={input.onChange}
          onBlur={input.onBlur}
          onFocus={input.onFocus}
        />
        {meta.touched && meta.error && <Text style={styles.error}>{meta.error}</Text>}
      </View>
    );
  }
}
```

### 3. Avoid Re-renders on Form State Changes

```tsx
// BAD - Subscribes to all form state
const mapStateToProps = (state: RootState) => ({
  formValues: state.form.myForm?.values, // Re-renders on any value change
});

// GOOD - Subscribe only to needed fields
import { formValueSelector } from 'redux-form';

const selector = formValueSelector('myForm');
const mapStateToProps = (state: RootState) => ({
  email: selector(state, 'email'),
  // Only re-renders when email changes
});
```

### 4. Partial Form Submission

```tsx
// Only validate/submit changed fields
const mapStateToProps = (state: RootState) => ({
  dirtyFields: state.form.myForm?.fields
    ? Object.keys(state.form.myForm.fields).filter(
        field => state.form.myForm!.fields[field].touched
      )
    : [],
});
```

## Redux Action Patterns

### 1. Action Creators

```tsx
// actions/userActions.ts
export const FETCH_USER_REQUEST = 'FETCH_USER_REQUEST';
export const FETCH_USER_SUCCESS = 'FETCH_USER_SUCCESS';
export const FETCH_USER_FAILURE = 'FETCH_USER_FAILURE';

export const fetchUser = (userId: string) => async (dispatch: Dispatch) => {
  dispatch({ type: FETCH_USER_REQUEST });

  try {
    const response = await api.get(`/users/${userId}`);
    dispatch({
      type: FETCH_USER_SUCCESS,
      payload: response.data,
    });
  } catch (error) {
    dispatch({
      type: FETCH_USER_FAILURE,
      payload: error.message,
    });
  }
};
```

### 2. Reducer Pattern

```tsx
// reducers/userReducer.ts
interface UserState {
  data: User | null;
  loading: boolean;
  error: string | null;
}

const initialState: UserState = {
  data: null,
  loading: false,
  error: null,
};

export default function userReducer(
  state = initialState,
  action: UserAction
): UserState {
  switch (action.type) {
    case FETCH_USER_REQUEST:
      return { ...state, loading: true, error: null };
    case FETCH_USER_SUCCESS:
      return { ...state, loading: false, data: action.payload };
    case FETCH_USER_FAILURE:
      return { ...state, loading: false, error: action.payload };
    default:
      return state;
  }
}
```

### 3. Avoid Action Spam

```tsx
// BAD - Dispatches on every keystroke
const handleChange = (text: string) => {
  dispatch(updateSearchQuery(text));
  dispatch(searchUsers(text)); // API call on every keystroke!
};

// GOOD - Debounce expensive operations
import debounce from 'lodash/debounce';

class SearchScreen extends Component {
  debouncedSearch = debounce((query: string) => {
    this.props.searchUsers(query);
  }, 300);

  handleChange = (text: string) => {
    this.props.updateSearchQuery(text); // Update local state immediately
    this.debouncedSearch(text); // Debounce API call
  };
}
```
