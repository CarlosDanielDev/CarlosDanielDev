# React Native Performance - mobile-app

## Preventing Re-renders

### 1. shouldComponentUpdate (Class Components)

```tsx
// mobile-app uses class components with connect()
class UserCard extends Component<Props> {
  shouldComponentUpdate(nextProps: Props) {
    // Only re-render if relevant props change
    return (
      this.props.user.id !== nextProps.user.id ||
      this.props.user.name !== nextProps.user.name ||
      this.props.user.avatar !== nextProps.user.avatar
    );
  }

  render() {
    const { user } = this.props;
    return (
      <View style={styles.card}>
        <Image source={{ uri: user.avatar }} />
        <Text>{user.name}</Text>
      </View>
    );
  }
}

export default connect(mapStateToProps)(UserCard);
```

### 2. PureComponent for Simple Props

```tsx
// Use PureComponent for shallow prop comparison
class UserListItem extends PureComponent<Props> {
  render() {
    const { user, onPress } = this.props;
    return (
      <TouchableOpacity onPress={() => onPress(user.id)}>
        <Text>{user.name}</Text>
      </TouchableOpacity>
    );
  }
}
```

### 3. React.memo for Functional Components

```tsx
// When using functional components (rare in mobile-app)
const UserBadge = memo(({ count }: { count: number }) => {
  return <Badge value={count} />;
});

// With custom comparison
const UserAvatar = memo(
  ({ user }: { user: User }) => <Avatar source={user.avatar} />,
  (prevProps, nextProps) => prevProps.user.avatar === nextProps.user.avatar
);
```

## FlatList Optimization

### 1. Essential Props

```tsx
class UserList extends Component<Props> {
  // Define outside render to prevent re-creation
  keyExtractor = (item: User) => item.id;

  getItemLayout = (_: any, index: number) => ({
    length: USER_ITEM_HEIGHT,
    offset: USER_ITEM_HEIGHT * index,
    index,
  });

  renderItem = ({ item }: { item: User }) => (
    <UserListItem user={item} onPress={this.props.onUserPress} />
  );

  render() {
    return (
      <FlatList
        data={this.props.users}
        keyExtractor={this.keyExtractor}
        renderItem={this.renderItem}
        getItemLayout={this.getItemLayout}
        // Performance props
        removeClippedSubviews={true}
        maxToRenderPerBatch={10}
        updateCellsBatchingPeriod={50}
        windowSize={5}
        initialNumToRender={10}
      />
    );
  }
}
```

### 2. Virtualized List Settings

| Prop | Purpose | Recommended Value |
|------|---------|-------------------|
| `removeClippedSubviews` | Unmount off-screen items | `true` |
| `maxToRenderPerBatch` | Items per batch | 10-15 |
| `windowSize` | Render window multiplier | 5-10 |
| `initialNumToRender` | Initial items | 10 |
| `updateCellsBatchingPeriod` | Batch update interval (ms) | 50 |

### 3. Avoid Anonymous Functions in renderItem

```tsx
// BAD - Creates new function every render
renderItem={({ item }) => (
  <Item
    data={item}
    onPress={() => this.handlePress(item.id)} // New function!
  />
)}

// GOOD - Use class method or memoized callback
class MyList extends Component {
  handlePress = (id: string) => {
    this.props.navigation.navigate('Detail', { id });
  };

  renderItem = ({ item }: { item: Item }) => (
    <Item data={item} onPress={this.handlePress} />
  );
}
```

## Image Optimization

### 1. Use FastImage

```tsx
import FastImage from 'react-native-fast-image';

<FastImage
  source={{
    uri: user.avatar,
    priority: FastImage.priority.normal,
    cache: FastImage.cacheControl.immutable,
  }}
  style={styles.avatar}
  resizeMode={FastImage.resizeMode.cover}
/>
```

### 2. Image Caching Strategy

```tsx
// Preload critical images
FastImage.preload([
  { uri: 'https://cdn.example.com/logo.png' },
  { uri: user.avatar },
]);

// Clear cache when needed
FastImage.clearMemoryCache();
FastImage.clearDiskCache();
```

## Startup Optimization

### 1. Lazy Load Non-Critical Screens

```tsx
// In navigation config
const HomeStack = createStackNavigator({
  Home: HomeScreen,
  // Lazy load secondary screens
  Settings: {
    getScreen: () => require('./SettingsScreen').default,
  },
  Profile: {
    getScreen: () => require('./ProfileScreen').default,
  },
});
```

### 2. Defer Non-Critical Operations

```tsx
class App extends Component {
  componentDidMount() {
    // Critical: Load immediately
    this.props.fetchUser();

    // Non-critical: Defer with InteractionManager
    InteractionManager.runAfterInteractions(() => {
      this.props.fetchNotifications();
      this.props.prefetchAssets();
    });
  }
}
```

### 3. Hermes Engine

Ensure Hermes is enabled in `android/app/build.gradle`:

```gradle
project.ext.react = [
    enableHermes: true
]
```

## Memory Management

### 1. Clean Up on Unmount

```tsx
class DataScreen extends Component {
  subscription: any = null;

  componentDidMount() {
    this.subscription = eventEmitter.addListener('event', this.handleEvent);
  }

  componentWillUnmount() {
    // Always clean up!
    if (this.subscription) {
      this.subscription.remove();
    }
  }
}
```

### 2. Avoid Memory Leaks in Async Operations

```tsx
class UserProfile extends Component {
  _isMounted = false;

  componentDidMount() {
    this._isMounted = true;
    this.loadData();
  }

  componentWillUnmount() {
    this._isMounted = false;
  }

  loadData = async () => {
    const data = await fetchUserData();
    // Check if component is still mounted
    if (this._isMounted) {
      this.setState({ data });
    }
  };
}
```

## Animation Performance

### 1. Use Native Driver

```tsx
Animated.timing(this.animatedValue, {
  toValue: 1,
  duration: 300,
  useNativeDriver: true, // Always use when possible
}).start();
```

### 2. Avoid Layout Animations with Native Driver

```tsx
// These properties DON'T support useNativeDriver: true
// - width, height
// - padding, margin
// - flex properties

// These DO support useNativeDriver: true
// - opacity
// - transform (translateX, translateY, scale, rotate)
```

## Debugging Performance

### 1. React DevTools Profiler

```bash
# Enable in development
npx react-devtools
```

### 2. Systrace (Android)

```bash
# Record trace
npx react-native run-android --variant=release
adb shell 'echo 1 > /sys/kernel/debug/tracing/tracing_on'
# ... reproduce issue ...
adb shell 'echo 0 > /sys/kernel/debug/tracing/tracing_on'
adb pull /sys/kernel/debug/tracing/trace ./trace.txt
```

### 3. Performance Monitor

```tsx
// Enable in dev menu or programmatically
import { NativeModules } from 'react-native';
NativeModules.PerfMonitor?.start();
```
