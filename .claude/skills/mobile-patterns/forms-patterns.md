# Forms Patterns for mobile-app

redux-form patterns and field components.

---

## Basic Form

```typescript
import { Field, reduxForm, InjectedFormProps } from 'redux-form'
import FieldInput from 'components/common/form/FieldInput'
import { generateTestID } from '../../util'

type FormData = {
  name: string
  email: string
  phone: string
}

const MyForm: React.FC<InjectedFormProps<FormData>> = ({ handleSubmit }) => (
  <View>
    <Field
      name="name"
      component={FieldInput}
      placeholder="Name"
      testProps={generateTestID('name-input')}
    />
    <Field
      name="email"
      component={FieldInput}
      placeholder="Email"
      keyboardType="email-address"
      testProps={generateTestID('email-input')}
    />
    <Field
      name="phone"
      component={FieldInput}
      placeholder="Phone"
      keyboardType="phone-pad"
      testProps={generateTestID('phone-input')}
    />
  </View>
)

export default reduxForm<FormData>({ form: 'myForm' })(MyForm)
```

---

## Form with Validation

```typescript
const validate = (values: FormData) => {
  const errors: Partial<FormData> = {}

  if (!values.name || values.name.trim() === '') {
    errors.name = 'Name is required'
  }

  if (!values.email) {
    errors.email = 'Email is required'
  } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(values.email)) {
    errors.email = 'Invalid email address'
  }

  if (!values.phone) {
    errors.phone = 'Phone is required'
  }

  return errors
}

export default reduxForm<FormData>({
  form: 'myForm',
  validate,
})(MyForm)
```

---

## Form with Initial Values

```typescript
import { connect } from 'react-redux'
import { reduxForm } from 'redux-form'

const MyForm = ({ handleSubmit, initialValues }) => (
  // Form fields
)

const MyFormWithRedux = reduxForm<FormData>({
  form: 'myForm',
  enableReinitialize: true, // Important for updates
})(MyForm)

const mapStateToProps = (state: RootState, ownProps: any) => ({
  initialValues: state.items.selected || {},
})

export default connect(mapStateToProps)(MyFormWithRedux)
```

---

## Custom Field Components

### FieldInput

```typescript
import React from 'react'
import { View, TextInput, StyleSheet } from 'react-native'
import { Text } from '@company/ui-components'
import colors from '@company/ui-components/src/packages/styles/colors'

type Props = {
  input: any
  meta: { touched: boolean; error?: string }
  placeholder: string
  testProps?: any
  keyboardType?: string
}

const FieldInput: React.FC<Props> = ({
  input,
  meta: { touched, error },
  placeholder,
  testProps,
  ...rest
}) => (
  <View style={styles.container}>
    <TextInput
      {...input}
      {...testProps}
      placeholder={placeholder}
      style={[styles.input, touched && error && styles.inputError]}
      onChangeText={input.onChange}
      onBlur={input.onBlur}
      onFocus={input.onFocus}
      value={input.value}
      {...rest}
    />
    {touched && error && (
      <Text style={styles.error}>{error}</Text>
    )}
  </View>
)

const styles = StyleSheet.create({
  container: { marginBottom: 16 },
  input: {
    borderWidth: 1,
    borderColor: colors.gray,
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  inputError: { borderColor: colors.error },
  error: { color: colors.error, fontSize: 12, marginTop: 4 },
})

export default FieldInput
```

### FieldPicker

```typescript
import React from 'react'
import { View } from 'react-native'
import { Picker } from '@react-native-picker/picker'
import { Text } from '@company/ui-components'

type Props = {
  input: any
  meta: { touched: boolean; error?: string }
  options: Array<{ label: string; value: string }>
  testProps?: any
}

const FieldPicker: React.FC<Props> = ({
  input,
  meta: { touched, error },
  options,
  testProps,
}) => (
  <View>
    <Picker
      {...testProps}
      selectedValue={input.value}
      onValueChange={input.onChange}
    >
      {options.map(option => (
        <Picker.Item
          key={option.value}
          label={option.label}
          value={option.value}
        />
      ))}
    </Picker>
    {touched && error && (
      <Text style={{ color: 'red' }}>{error}</Text>
    )}
  </View>
)

export default FieldPicker
```

---

## Submitting Form from Screen

```typescript
import { submit } from 'redux-form'
import { connect } from 'react-redux'

const MyScreen: React.FC<Props> = ({ submitForm, saveData }) => {
  const handleSave = async (values: FormData) => {
    try {
      await saveData(values)
      Alert.alert('Success')
    } catch (error) {
      Alert.alert('Error')
    }
  }

  return (
    <Screen
      navigation={navigation}
      title="Form"
      rightButtons={[
        { icon: 'save', onPress: submitForm }
      ]}
    >
      <MyForm onSubmit={handleSave} />
    </Screen>
  )
}

const mapDispatchToProps = {
  submitForm: () => submit('myForm'),
  saveData,
}

export default connect(null, mapDispatchToProps)(MyScreen)
```

---

## Form State in Redux

```typescript
import { formValueSelector } from 'redux-form'

const selector = formValueSelector('myForm')

const mapStateToProps = (state: RootState) => ({
  nameValue: selector(state, 'name'),
  emailValue: selector(state, 'email'),
})

// Access form values in component
const { nameValue, emailValue } = props
```

---

## Resetting Form

```typescript
import { reset } from 'redux-form'

const mapDispatchToProps = {
  resetForm: () => reset('myForm'),
}

// In component
props.resetForm()
```

---

## Field Arrays (Dynamic Lists)

```typescript
import { FieldArray } from 'redux-form'

const renderItems = ({ fields }) => (
  <View>
    {fields.map((item, index) => (
      <View key={index}>
        <Field
          name={`${item}.name`}
          component={FieldInput}
          placeholder="Item name"
        />
        <Button onPress={() => fields.remove(index)}>
          Remove
        </Button>
      </View>
    ))}
    <Button onPress={() => fields.push({})}>
      Add Item
    </Button>
  </View>
)

const MyForm = () => (
  <View>
    <FieldArray name="items" component={renderItems} />
  </View>
)
```
