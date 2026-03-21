# Form Pattern (mobile-app)

This pattern is based on the form implementation used in `mobile-app` using **react-hook-form**.

## Overview

The mobile-app uses `react-hook-form` for form management with:
- `useForm` hook for form state management
- `formMethods.handleSubmit` for form submission
- `formMethods.watch` for reactive field values
- `formMethods.formState` for form state (isDirty, errors, etc.)
- Integration with `connect()` for Redux actions

## Basic Form Setup

```typescript
import React from 'react'
import { connect } from 'react-redux'
import { useForm } from 'react-hook-form'

interface FormData {
  name: string
  email: string
  active: boolean
}

const MyFormScreen = ({ saveData, navigation, uid, store }) => {
  const formMethods = useForm<FormData>({
    defaultValues: {
      name: '',
      email: '',
      active: true,
    },
  })

  const handleSave = ({ data }: { data: FormData }) => {
    saveData(
      {
        ...data,
        uid,
        aid: store.aid,
      },
      (error: any) => {
        if (error) {
          // Handle error
          return
        }
        navigation.goBack()
      }
    )
  }

  return (
    <View>
      {/* Form fields */}
      <Button
        onPress={formMethods.handleSubmit((data) => handleSave({ data }))}
        disabled={!formMethods.formState.isDirty}
      >
        Save
      </Button>
    </View>
  )
}

export default connect(
  ({ auth }) => ({
    store: auth.store,
    uid: auth.user.uid,
  }),
  { saveData }
)(MyFormScreen)
```

## Form with Default Values from Props

```typescript
import React from 'react'
import { connect } from 'react-redux'
import { useForm } from 'react-hook-form'
import { useRoute } from '@react-navigation/native'

interface FormData {
  active: boolean
  code: string
}

const EditScreen = ({ editItem, navigation, uid, store }) => {
  const route = useRoute()
  const item = (route.params?.item || {}) as IItem

  const formMethods = useForm<FormData>({
    defaultValues: {
      active: item.active,
      code: item.code,
    },
  })

  // Watch specific field for reactive UI updates
  const isActive = formMethods.watch('active')

  const handleSave = ({ data }: { data: FormData }) => {
    editItem(
      {
        item: {
          ...item,
          ...data,
        },
        uid,
        aid: store.aid,
      },
      (error: any) => {
        if (error) {
          // Show error notification
          return
        }
        navigation.replace('ItemsList', { itemUpdated: true })
      }
    )
  }

  return (
    <DetailPage pageTitle={item.code} goBack={() => navigation.goBack()}>
      <ScrollView>
        {/* Conditional rendering based on watched value */}
        {isActive && <ActiveContent />}

        <MyFormField formMethods={formMethods} item={item} />
      </ScrollView>

      <ActionButton
        onPress={formMethods.handleSubmit((data) => handleSave({ data }))}
        disabled={!formMethods.formState.isDirty}
      >
        Save
      </ActionButton>
    </DetailPage>
  )
}

export default connect(
  ({ auth }) => ({
    store: auth.store,
    uid: auth.user.uid,
  }),
  { editItem }
)(EditScreen)
```

## Form Field Component Pattern

Form fields receive `formMethods` as prop and use Controller or register:

```typescript
import React from 'react'
import { Controller, UseFormReturn } from 'react-hook-form'
import { Switch, Text, View } from 'react-native'

interface Props {
  formMethods: UseFormReturn<FormData>
  item: IItem
}

const MyFormField = ({ formMethods, item }: Props) => {
  const { control, formState: { errors } } = formMethods

  return (
    <View>
      <Controller
        control={control}
        name="active"
        render={({ field: { onChange, value } }) => (
          <View>
            <Text>Active</Text>
            <Switch
              value={value}
              onValueChange={onChange}
            />
          </View>
        )}
      />
      {errors.active && <Text style={{ color: 'red' }}>{errors.active.message}</Text>}
    </View>
  )
}

export default MyFormField
```

## Form with Validation

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const formSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
  amount: z.number().min(0, 'Amount must be positive'),
})

type FormData = z.infer<typeof formSchema>

const MyValidatedForm = () => {
  const formMethods = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      email: '',
      amount: 0,
    },
  })

  const {
    handleSubmit,
    formState: { errors, isDirty, isValid },
  } = formMethods

  return (
    <View>
      {/* Form fields with error display */}
      <Button
        onPress={handleSubmit(onSubmit)}
        disabled={!isDirty || !isValid}
      >
        Submit
      </Button>
    </View>
  )
}
```

## Key Form Methods

### `useForm` Options

```typescript
const formMethods = useForm<FormData>({
  defaultValues: {
    // Initial values for all fields
  },
  resolver: zodResolver(schema), // Optional: validation resolver
  mode: 'onChange', // When to validate: 'onBlur' | 'onChange' | 'onSubmit'
})
```

### Common `formMethods` Properties

```typescript
const {
  // Core methods
  handleSubmit,    // Wrap submit handler: handleSubmit((data) => ...)
  watch,           // Watch field value: watch('fieldName') or watch() for all
  reset,           // Reset form: reset() or reset(newValues)
  setValue,        // Set single field: setValue('field', value)
  getValues,       // Get current values: getValues() or getValues('field')
  trigger,         // Trigger validation: trigger() or trigger('field')

  // Form state
  formState: {
    isDirty,       // Form has been modified
    isValid,       // All validations pass
    errors,        // Validation errors object
    isSubmitting,  // Form is being submitted
    dirtyFields,   // Object of dirty fields
    touchedFields, // Object of touched fields
  },

  // For Controller
  control,         // Pass to Controller component
} = formMethods
```

## Integration with Redux `connect()`

**IMPORTANT:** Always use `connect()` HOC, not Redux hooks.

```typescript
import { connect } from 'react-redux'
import { useForm } from 'react-hook-form'

const MyScreen = ({
  // Redux state
  store,
  uid,
  loader,
  // Redux actions
  saveAction,
  navigation,
}) => {
  const formMethods = useForm<FormData>({
    defaultValues: { ... }
  })

  const onSubmit = (data: FormData) => {
    saveAction(
      {
        ...data,
        uid,
        aid: store.aid,
      },
      (error) => {
        if (error) {
          // Handle error
          return
        }
        navigation.goBack()
      }
    )
  }

  return (
    <View>
      {loader && <LoadingScreen />}
      {/* Form content */}
      <Button onPress={formMethods.handleSubmit(onSubmit)}>
        Save
      </Button>
    </View>
  )
}

export default connect(
  ({ auth, common }) => ({
    store: auth.store,
    uid: auth.user.uid,
    loader: common.loader.visible,
  }),
  { saveAction }
)(MyScreen)
```

## Key Rules

1. **Use `useForm` hook** - Always initialize with `useForm<FormData>()`
2. **Pass `formMethods` to child components** - Don't create multiple form instances
3. **Use `handleSubmit` wrapper** - Always wrap submit handler with `formMethods.handleSubmit()`
4. **Check `isDirty` for save button** - Disable save when form hasn't changed
5. **Use `watch` for reactive UI** - When UI depends on field values
6. **Combine with `connect()`** - Use Redux connect for state and actions
7. **Callback pattern for async** - Pass callback to Redux actions for success/error handling
