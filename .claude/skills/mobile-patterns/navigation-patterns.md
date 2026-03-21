# Navigation Patterns for mobile-app

React Navigation setup and patterns.

---

## Navigation Hook

```typescript
import { useNavigation } from '@react-navigation/native'

const MyComponent = () => {
  const navigation = useNavigation()

  return (
    <Button onPress={() => navigation.navigate('ScreenName')}>
      Go to Screen
    </Button>
  )
}
```

---

## Navigation with Params

```typescript
// Navigate with params
navigation.navigate('ProductDetail', { productId: '123' })

// Access params in target screen
const ProductDetailScreen: React.FC<Props> = ({ route }) => {
  const { productId } = route.params || {}

  useEffect(() => {
    if (productId) {
      fetchProduct(productId)
    }
  }, [productId])
}
```

---

## Stack Navigator

```typescript
import { createStackNavigator } from '@react-navigation/stack'

const Stack = createStackNavigator()

const ProductStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="ProductList" component={ProductListScreen} />
    <Stack.Screen name="ProductDetail" component={ProductDetailScreen} />
    <Stack.Screen name="ProductEdit" component={ProductEditScreen} />
  </Stack.Navigator>
)
```

---

## Tab Navigator

```typescript
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'

const Tab = createBottomTabNavigator()

const MainTabs = () => (
  <Tab.Navigator>
    <Tab.Screen name="Home" component={HomeScreen} />
    <Tab.Screen name="Products" component={ProductStack} />
    <Tab.Screen name="Settings" component={SettingsScreen} />
  </Tab.Navigator>
)
```

---

## Deep Linking

```typescript
// App.tsx
const linking = {
  prefixes: ['myapp://'],
  config: {
    screens: {
      ProductDetail: 'products/:productId',
      OrderDetail: 'orders/:orderId',
    },
  },
}

<NavigationContainer linking={linking}>
  {/* Navigation structure */}
</NavigationContainer>
```

---

## Back Navigation

```typescript
// Go back
navigation.goBack()

// Go back to specific screen
navigation.navigate('ScreenName')

// Reset navigation stack
navigation.reset({
  index: 0,
  routes: [{ name: 'Home' }],
})
```

---

## Navigation in Screen

```typescript
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
```
