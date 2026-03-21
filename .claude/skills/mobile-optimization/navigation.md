# React Navigation Patterns - mobile-app

## Lazy Loading Screens

### 1. Dynamic Import for Heavy Screens

```tsx
import { createStackNavigator } from '@react-navigation/stack';

const Stack = createStackNavigator();

// Lazy load non-critical screens
const SettingsScreen = React.lazy(() => import('./screens/SettingsScreen'));
const ProfileScreen = React.lazy(() => import('./screens/ProfileScreen'));
const AnalyticsScreen = React.lazy(() => import('./screens/AnalyticsScreen'));

function AppNavigator() {
  return (
    <Stack.Navigator>
      {/* Critical screens - load immediately */}
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen name="Dashboard" component={DashboardScreen} />

      {/* Non-critical screens - lazy load */}
      <Stack.Screen
        name="Settings"
        component={SettingsScreen}
        options={{ lazy: true }}
      />
      <Stack.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ lazy: true }}
      />
    </Stack.Navigator>
  );
}
```

### 2. Deferred Screen Loading

```tsx
// Only load screen content after navigation animation completes
class HeavyScreen extends Component {
  state = { isReady: false };

  componentDidMount() {
    // Wait for navigation animation to complete
    InteractionManager.runAfterInteractions(() => {
      this.setState({ isReady: true });
    });
  }

  render() {
    if (!this.state.isReady) {
      return <ScreenPlaceholder />;
    }
    return <HeavyContent />;
  }
}
```

## Preloading Data

### 1. Prefetch on Focus

```tsx
class ProductListScreen extends Component {
  componentDidMount() {
    // Add focus listener
    this.unsubscribe = this.props.navigation.addListener('focus', () => {
      this.prefetchNextScreen();
    });
  }

  componentWillUnmount() {
    this.unsubscribe?.();
  }

  prefetchNextScreen = () => {
    // Prefetch data for likely next screen
    const firstProductId = this.props.products[0]?.id;
    if (firstProductId) {
      this.props.prefetchProductDetails(firstProductId);
    }
  };
}
```

### 2. Preload on Long Press

```tsx
class ProductListItem extends Component {
  handleLongPress = () => {
    // Preload product details on long press (user likely to navigate)
    this.props.prefetchProductDetails(this.props.product.id);
  };

  handlePress = () => {
    this.props.navigation.navigate('ProductDetails', {
      productId: this.props.product.id,
    });
  };

  render() {
    return (
      <TouchableOpacity
        onPress={this.handlePress}
        onLongPress={this.handleLongPress}
        delayLongPress={200}
      >
        <ProductCard product={this.props.product} />
      </TouchableOpacity>
    );
  }
}
```

## Navigation Performance

### 1. Optimize Tab Navigator

```tsx
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        // Don't unmount inactive screens
        lazy: false,
        // But do unmount if memory pressure
        unmountOnBlur: false,
        // Freeze inactive screens
        freezeOnBlur: true,
      }}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Search" component={SearchScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}
```

### 2. Optimize Stack Navigator

```tsx
const Stack = createStackNavigator();

function AppStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        // Use native animations
        animation: 'default',
        // Optimize header
        headerMode: 'screen',
        // Don't remount on focus
        detachPreviousScreen: false,
      }}
    >
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen
        name="Details"
        component={DetailsScreen}
        options={{
          // Optimize transition
          presentation: 'card',
          animationTypeForReplace: 'push',
        }}
      />
    </Stack.Navigator>
  );
}
```

### 3. Avoid Re-renders on Navigation State Changes

```tsx
// BAD - Re-renders on any navigation state change
class MyScreen extends Component {
  render() {
    const { navigation } = this.props;
    // Accessing navigation.state triggers re-renders
    const currentRoute = navigation.state.routeName;
    return <View />;
  }
}

// GOOD - Use navigation listeners
class MyScreen extends Component {
  state = { isFocused: false };

  componentDidMount() {
    this.focusListener = this.props.navigation.addListener('focus', () => {
      this.setState({ isFocused: true });
    });
    this.blurListener = this.props.navigation.addListener('blur', () => {
      this.setState({ isFocused: false });
    });
  }

  componentWillUnmount() {
    this.focusListener?.();
    this.blurListener?.();
  }
}
```

## Deep Linking

### 1. Configuration

```tsx
// navigation/linking.ts
export const linking = {
  prefixes: ['myapp://', 'https://app.example.com'],
  config: {
    screens: {
      Home: 'home',
      Product: {
        path: 'product/:id',
        parse: {
          id: (id: string) => id,
        },
      },
      Profile: 'profile/:userId',
      Settings: 'settings',
    },
  },
};

// App.tsx
<NavigationContainer linking={linking} fallback={<SplashScreen />}>
  <AppNavigator />
</NavigationContainer>
```

### 2. Handle Deep Links in Running App

```tsx
import { Linking } from 'react-native';

class App extends Component {
  componentDidMount() {
    // Handle deep link when app is running
    Linking.addEventListener('url', this.handleDeepLink);

    // Handle deep link that opened the app
    Linking.getInitialURL().then(url => {
      if (url) {
        this.handleDeepLink({ url });
      }
    });
  }

  componentWillUnmount() {
    Linking.removeEventListener('url', this.handleDeepLink);
  }

  handleDeepLink = ({ url }: { url: string }) => {
    // Parse and navigate
    const route = parseDeepLink(url);
    if (route) {
      this.props.navigation.navigate(route.name, route.params);
    }
  };
}
```

### 3. Universal Links (iOS) / App Links (Android)

```tsx
// Verify domain ownership for universal links
// iOS: apple-app-site-association file on your domain
// Android: assetlinks.json on your domain

// Handle in App
const handleUniversalLink = async (url: string) => {
  const parsed = parseUniversalLink(url);

  if (parsed.type === 'product') {
    // Prefetch data before navigating
    await store.dispatch(fetchProduct(parsed.id));
    navigation.navigate('Product', { id: parsed.id });
  }
};
```

## Navigation State Persistence

### 1. Save/Restore Navigation State

```tsx
import AsyncStorage from '@react-native-async-storage/async-storage';

const NAVIGATION_STATE_KEY = 'NAVIGATION_STATE';

function App() {
  const [isReady, setIsReady] = useState(false);
  const [initialState, setInitialState] = useState();

  useEffect(() => {
    const restoreState = async () => {
      try {
        const savedState = await AsyncStorage.getItem(NAVIGATION_STATE_KEY);
        if (savedState) {
          setInitialState(JSON.parse(savedState));
        }
      } finally {
        setIsReady(true);
      }
    };

    if (!isReady) {
      restoreState();
    }
  }, [isReady]);

  if (!isReady) {
    return <SplashScreen />;
  }

  return (
    <NavigationContainer
      initialState={initialState}
      onStateChange={state =>
        AsyncStorage.setItem(NAVIGATION_STATE_KEY, JSON.stringify(state))
      }
    >
      <AppNavigator />
    </NavigationContainer>
  );
}
```

## Common Navigation Pitfalls

### 1. Passing Large Objects

```tsx
// BAD - Passing entire object through navigation
navigation.navigate('ProductDetails', { product: largeProductObject });

// GOOD - Pass only ID, fetch in target screen
navigation.navigate('ProductDetails', { productId: product.id });
```

### 2. Navigation in componentDidMount Race Conditions

```tsx
// BAD - Navigation might fail if screen not fully mounted
componentDidMount() {
  this.props.navigation.navigate('NextScreen');
}

// GOOD - Wait for layout
componentDidMount() {
  InteractionManager.runAfterInteractions(() => {
    this.props.navigation.navigate('NextScreen');
  });
}
```

### 3. Memory Leaks with Navigation Listeners

```tsx
class MyScreen extends Component {
  focusListener = null;

  componentDidMount() {
    this.focusListener = this.props.navigation.addListener('focus', () => {
      this.loadData();
    });
  }

  componentWillUnmount() {
    // ALWAYS remove listeners!
    if (this.focusListener) {
      this.focusListener();
    }
  }
}
```
