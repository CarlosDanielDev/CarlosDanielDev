# Common Components for mobile-app

Reusable components from ui-components and common/.

---

## Screen

Main screen wrapper with header.

```typescript
import Screen from 'components/common/Screen'

const MyScreen = ({ navigation }) => (
  <Screen
    navigation={navigation}
    title="Screen Title"
    rightButtons={[
      {
        icon: 'add',
        onPress: () => navigation.navigate('AddItem')
      },
      {
        icon: 'search',
        onPress: handleSearch
      }
    ]}
    leftButton={{
      icon: 'back',
      onPress: () => navigation.goBack()
    }}
  >
    {/* Screen content */}
  </Screen>
)
```

---

## Modal

Modal wrapper with buttons.

```typescript
import Modal from 'components/common/Modal'

const MyModal = ({ isVisible, hideModal, onConfirm }) => (
  <Modal
    isVisible={isVisible}
    hideModal={hideModal}
    title="Confirm Action"
    modalButtons={[
      {
        title: 'Cancel',
        onPress: hideModal,
        ...generateTestID('cancel-button')
      },
      {
        title: 'Confirm',
        onPress: onConfirm,
        ...generateTestID('confirm-button')
      }
    ]}
  >
    <Container padding={20}>
      <Text>Are you sure?</Text>
    </Container>
  </Modal>
)
```

---

## UI Components from ui-components

### Container

```typescript
import { Container } from '@company/ui-components'

<Container padding={20} backgroundColor="#fff">
  {/* Content */}
</Container>
```

### Text

```typescript
import { Text } from '@company/ui-components'

<Text
  {...generateTestID('my-text')}
  style={{ fontSize: 16, color: '#333' }}
>
  Hello World
</Text>
```

### Button

```typescript
import { Button } from '@company/ui-components'

<Button
  {...generateTestID('save-button')}
  onPress={handleSave}
  disabled={loading}
>
  Save
</Button>
```

### Icon

```typescript
import { Icon } from '@company/ui-components'

<Icon name="add" size={24} color="#000" />
```

---

## Colors

```typescript
import colors from '@company/ui-components/src/packages/styles/colors'

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.white,
  },
  text: {
    color: colors.primary,
  },
  error: {
    color: colors.error,
  },
})
```

Available colors:
- `colors.primary`
- `colors.secondary`
- `colors.success`
- `colors.error`
- `colors.warning`
- `colors.gray`
- `colors.lightGray`
- `colors.white`
- `colors.black`

---

## Loading Indicator

```typescript
import { ActivityIndicator, View } from 'react-native'
import colors from '@company/ui-components/src/packages/styles/colors'

{loading && (
  <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color={colors.primary} />
  </View>
)}
```

---

## Empty State

```typescript
import { Text } from '@company/ui-components'

{items.length === 0 && !loading && (
  <View style={styles.emptyState}>
    <Text {...generateTestID('empty-state')}>
      No items found
    </Text>
  </View>
)}
```

---

## Error Message

```typescript
{error && (
  <View style={styles.errorContainer}>
    <Text
      {...generateTestID('error-message')}
      style={{ color: colors.error }}
    >
      {error}
    </Text>
  </View>
)}
```
