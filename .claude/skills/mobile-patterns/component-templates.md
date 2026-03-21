# Component Templates for mobile-app

Complete component boilerplates ready to use.

---

## Screen Component Template

```typescript
import React, { useEffect, useCallback } from 'react'
import { View, Alert } from 'react-native'
import { Container, Text, Button } from '@company/ui-components'
import { connect } from 'react-redux'
import { someAction, anotherAction } from '../stores/actions'
import { NavigationProp } from '@react-navigation/native'
import { RootState } from '../types/state/RootState'
import { generateTestID } from '../../util'
import I18n from '../../i18n/i18n'
import Screen from 'components/common/Screen'

// Internationalization strings
const Strings = {
  t_title: I18n.t('myScreen.title'),
  t_description: I18n.t('myScreen.description'),
  t_buttonLabel: I18n.t('myScreen.buttonLabel'),
}

// Type definitions
type StateProps = ReturnType<typeof mapStateToProps>

type ActionProps = {
  someAction: typeof someAction
  anotherAction: typeof anotherAction
}

type OwnProps = {
  navigation: NavigationProp<any>
  route: any
}

type Props = StateProps & ActionProps & OwnProps

// Component
const MyScreen: React.FC<Props> = ({
  navigation,
  route,
  user,
  data,
  loading,
  someAction,
  anotherAction,
}) => {
  // Fetch data on mount
  useEffect(() => {
    someAction({ userId: user.id })
  }, [user.id, someAction])

  // Handler with navigation
  const handlePress = useCallback(() => {
    navigation.navigate('DetailScreen', { id: '123' })
  }, [navigation])

  // Handler with async action
  const handleSave = useCallback(async () => {
    try {
      await anotherAction({ data: 'some data' })
      Alert.alert('Success', 'Saved successfully')
    } catch (error) {
      Alert.alert('Error', 'Failed to save')
    }
  }, [anotherAction])

  return (
    <Screen
      navigation={navigation}
      title={Strings.t_title}
      rightButtons={[
        { icon: 'add', onPress: handlePress }
      ]}
    >
      <Container padding={20}>
        <Text {...generateTestID('screen-title')}>
          {Strings.t_description}
        </Text>

        {loading ? (
          <Text>Loading...</Text>
        ) : (
          <Button
            {...generateTestID('save-button')}
            onPress={handleSave}
          >
            {Strings.t_buttonLabel}
          </Button>
        )}
      </Container>
    </Screen>
  )
}

// Redux connection
const mapStateToProps = (state: RootState) => ({
  user: state.auth.user,
  data: state.myFeature.data,
  loading: state.myFeature.loading,
})

const mapDispatchToProps = {
  someAction,
  anotherAction,
}

export default connect(mapStateToProps, mapDispatchToProps)(MyScreen)
```

---

## Modal Component Template

```typescript
import React from 'react'
import { View } from 'react-native'
import { Text, Container } from '@company/ui-components'
import Modal from 'components/common/Modal'
import { generateTestID } from '../../util'
import I18n from '../../i18n/i18n'

const Strings = {
  t_title: I18n.t('myModal.title'),
  t_description: I18n.t('myModal.description'),
  t_cancel: I18n.t('common.cancel'),
  t_confirm: I18n.t('common.confirm'),
}

type Props = {
  isVisible: boolean
  hideModal: () => void
  onConfirm: () => void
  data?: any
}

const MyModal: React.FC<Props> = ({
  isVisible,
  hideModal,
  onConfirm,
  data,
}) => {
  const handleConfirm = () => {
    onConfirm()
    hideModal()
  }

  return (
    <Modal
      isVisible={isVisible}
      hideModal={hideModal}
      title={Strings.t_title}
      modalButtons={[
        {
          title: Strings.t_cancel,
          onPress: hideModal,
          ...generateTestID('cancel-button'),
        },
        {
          title: Strings.t_confirm,
          onPress: handleConfirm,
          ...generateTestID('confirm-button'),
        },
      ]}
    >
      <Container padding={20}>
        <Text {...generateTestID('modal-content')}>
          {Strings.t_description}
        </Text>
        {data && (
          <Text {...generateTestID('modal-data')}>
            {JSON.stringify(data)}
          </Text>
        )}
      </Container>
    </Modal>
  )
}

export default MyModal
```

---

## List Item Component Template

```typescript
import React, { memo } from 'react'
import { TouchableOpacity, View, StyleSheet } from 'react-native'
import { Text } from '@company/ui-components'
import colors from '@company/ui-components/src/packages/styles/colors'
import { generateTestID } from '../../util'

type Props = {
  item: {
    id: string
    name: string
    description: string
    status: string
  }
  onPress: (id: string) => void
  index: number
}

const ListItem: React.FC<Props> = ({ item, onPress, index }) => {
  return (
    <TouchableOpacity
      {...generateTestID(`list-item-${index}`)}
      onPress={() => onPress(item.id)}
      style={styles.container}
    >
      <View style={styles.content}>
        <Text
          {...generateTestID(`item-name-${index}`)}
          style={styles.name}
        >
          {item.name}
        </Text>
        <Text
          {...generateTestID(`item-description-${index}`)}
          style={styles.description}
        >
          {item.description}
        </Text>
      </View>
      <Text
        {...generateTestID(`item-status-${index}`)}
        style={[
          styles.status,
          { color: item.status === 'active' ? colors.success : colors.gray }
        ]}
      >
        {item.status}
      </Text>
    </TouchableOpacity>
  )
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.lightGray,
  },
  content: {
    flex: 1,
  },
  name: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  description: {
    fontSize: 14,
    color: colors.gray,
  },
  status: {
    fontSize: 12,
    textTransform: 'uppercase',
  },
})

// Use memo to prevent unnecessary re-renders
export default memo(ListItem)
```

---

## FlatList Screen Template

```typescript
import React, { useEffect, useCallback } from 'react'
import { FlatList } from 'react-native'
import { Container } from '@company/ui-components'
import { connect } from 'react-redux'
import { fetchItems } from '../stores/actions'
import { NavigationProp } from '@react-navigation/native'
import { RootState } from '../types/state/RootState'
import { generateTestID } from '../../util'
import Screen from 'components/common/Screen'
import ListItem from './ListItem'

type StateProps = ReturnType<typeof mapStateToProps>
type ActionProps = { fetchItems: typeof fetchItems }
type OwnProps = { navigation: NavigationProp<any> }
type Props = StateProps & ActionProps & OwnProps

const ITEM_HEIGHT = 80

const ListScreen: React.FC<Props> = ({
  navigation,
  items,
  loading,
  fetchItems,
}) => {
  useEffect(() => {
    fetchItems({})
  }, [fetchItems])

  const handleItemPress = useCallback((id: string) => {
    navigation.navigate('DetailScreen', { id })
  }, [navigation])

  const keyExtractor = useCallback((item: any) => item.id, [])

  const getItemLayout = useCallback(
    (_: any, index: number) => ({
      length: ITEM_HEIGHT,
      offset: ITEM_HEIGHT * index,
      index,
    }),
    []
  )

  const renderItem = useCallback(
    ({ item, index }: any) => (
      <ListItem item={item} onPress={handleItemPress} index={index} />
    ),
    [handleItemPress]
  )

  return (
    <Screen
      navigation={navigation}
      title="Items"
      rightButtons={[
        { icon: 'add', onPress: () => navigation.navigate('AddItem') }
      ]}
    >
      <Container>
        <FlatList
          {...generateTestID('items-list')}
          data={items}
          keyExtractor={keyExtractor}
          renderItem={renderItem}
          getItemLayout={getItemLayout}
          removeClippedSubviews={true}
          maxToRenderPerBatch={10}
          windowSize={5}
          initialNumToRender={10}
          refreshing={loading}
          onRefresh={() => fetchItems({})}
        />
      </Container>
    </Screen>
  )
}

const mapStateToProps = (state: RootState) => ({
  items: state.items.list,
  loading: state.items.loading,
})

const mapDispatchToProps = { fetchItems }

export default connect(mapStateToProps, mapDispatchToProps)(ListScreen)
```

---

## Form Screen Template

```typescript
import React, { useCallback } from 'react'
import { Alert } from 'react-native'
import { Container } from '@company/ui-components'
import { connect } from 'react-redux'
import { submit } from 'redux-form'
import { saveItem } from '../stores/actions'
import { NavigationProp } from '@react-navigation/native'
import Screen from 'components/common/Screen'
import MyForm from './MyForm'

type ActionProps = {
  submitForm: () => void
  saveItem: typeof saveItem
}

type OwnProps = {
  navigation: NavigationProp<any>
  route: any
}

type Props = ActionProps & OwnProps

const FormScreen: React.FC<Props> = ({
  navigation,
  route,
  submitForm,
  saveItem,
}) => {
  const isEdit = route.params?.id

  const handleSubmit = useCallback(async (values: any) => {
    try {
      await saveItem(values)
      Alert.alert('Success', 'Item saved successfully')
      navigation.goBack()
    } catch (error) {
      Alert.alert('Error', 'Failed to save item')
    }
  }, [saveItem, navigation])

  return (
    <Screen
      navigation={navigation}
      title={isEdit ? 'Edit Item' : 'Add Item'}
      rightButtons={[
        { icon: 'save', onPress: submitForm }
      ]}
    >
      <Container padding={20}>
        <MyForm onSubmit={handleSubmit} />
      </Container>
    </Screen>
  )
}

const mapDispatchToProps = {
  submitForm: () => submit('myForm'),
  saveItem,
}

export default connect(null, mapDispatchToProps)(FormScreen)
```

---

## Usage Guidelines

1. **Copy the template** that matches your needs
2. **Replace placeholder names** (MyScreen, myFeature, etc.)
3. **Add internationalization strings** to i18n files
4. **Implement actions/reducers** as needed
5. **Add testIDs** to all interactive elements
6. **Test on both iOS and Android**

---

## Testing Template

Every component should have corresponding test IDs:

```typescript
// Screen
generateTestID('my-screen')

// Buttons
generateTestID('save-button')
generateTestID('cancel-button')
generateTestID('add-button')

// Inputs
generateTestID('name-input')
generateTestID('email-input')

// Lists
generateTestID('items-list')
generateTestID('list-item-0')
generateTestID('list-item-1')

// Text/Content
generateTestID('screen-title')
generateTestID('error-message')
```
