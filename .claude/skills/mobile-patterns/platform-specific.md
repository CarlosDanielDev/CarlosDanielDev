# Platform-Specific Patterns for mobile-app

Handling iOS and Android differences.

---

## Platform.select()

```typescript
import { Platform } from 'react-native'

const MyComponent = () => {
  const containerStyle = Platform.select({
    ios: {
      backgroundColor: '#FFFFFF',
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    },
    android: {
      backgroundColor: 'transparent',
      elevation: 3,
    },
  })

  return <View style={containerStyle}>{/* ... */}</View>
}
```

---

## Platform-Specific Code

```typescript
if (Platform.OS === 'ios') {
  // iOS-specific code
} else if (Platform.OS === 'android') {
  // Android-specific code
}
```

---

## Platform-Specific Files

Create separate files:
- `Component.ios.tsx` - iOS implementation
- `Component.android.tsx` - Android implementation

Import normally:
```typescript
import Component from './Component' // Auto-picks correct file
```

---

## Safe Area

```typescript
import { SafeAreaView } from 'react-native-safe-area-context'

const MyScreen = () => (
  <SafeAreaView style={{ flex: 1 }}>
    {/* Content respects notch/status bar */}
  </SafeAreaView>
)
```

---

## Status Bar

```typescript
import { StatusBar } from 'react-native'

<StatusBar
  barStyle={Platform.OS === 'ios' ? 'dark-content' : 'light-content'}
  backgroundColor={Platform.OS === 'android' ? colors.primary : undefined}
/>
```

---

## Keyboard Handling

### iOS vs Android

```typescript
import { KeyboardAvoidingView, Platform } from 'react-native'

<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
  style={{ flex: 1 }}
>
  {/* Form inputs */}
</KeyboardAvoidingView>
```

### Dismiss Keyboard

```typescript
import { Keyboard } from 'react-native'

const dismissKeyboard = () => {
  Keyboard.dismiss()
}
```

---

## Gestures

### Swipe (iOS)

```typescript
import { GestureDetector, Gesture } from 'react-native-gesture-handler'

const swipe = Gesture.Fling()
  .direction(Directions.LEFT)
  .onEnd(() => {
    // Handle swipe
  })

<GestureDetector gesture={swipe}>
  <View>{/* Content */}</View>
</GestureDetector>
```

### Long Press

```typescript
import { TouchableOpacity } from 'react-native'

<TouchableOpacity
  onPress={handlePress}
  onLongPress={handleLongPress}
  delayLongPress={500}
>
  {/* Content */}
</TouchableOpacity>
```

---

## Permissions

```typescript
import { PermissionsAndroid, Platform } from 'react-native'

const requestCameraPermission = async () => {
  if (Platform.OS === 'android') {
    const granted = await PermissionsAndroid.request(
      PermissionsAndroid.PERMISSIONS.CAMERA
    )
    return granted === PermissionsAndroid.RESULTS.GRANTED
  }
  // iOS permissions handled in Info.plist
  return true
}
```

---

## Linking

```typescript
import { Linking, Platform } from 'react-native'

const openURL = (url: string) => {
  Linking.canOpenURL(url).then(supported => {
    if (supported) {
      Linking.openURL(url)
    }
  })
}

// Open phone dialer
const callPhone = (number: string) => {
  const url = Platform.OS === 'ios' ? `telprompt:${number}` : `tel:${number}`
  openURL(url)
}

// Open email
const sendEmail = (email: string) => {
  openURL(`mailto:${email}`)
}
```

---

## Device Info

```typescript
import { Dimensions, Platform } from 'react-native'

const { width, height } = Dimensions.get('window')

const isSmallDevice = width < 375
const isTablet = width > 768

const isIOS = Platform.OS === 'ios'
const isAndroid = Platform.OS === 'android'
```

---

## Haptic Feedback (iOS)

```typescript
import ReactNativeHapticFeedback from 'react-native-haptic-feedback'

const triggerHaptic = () => {
  if (Platform.OS === 'ios') {
    ReactNativeHapticFeedback.trigger('impactLight')
  }
}
```

---

## Shadow vs Elevation

```typescript
const styles = StyleSheet.create({
  card: {
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 3.84,
      },
      android: {
        elevation: 5,
      },
    }),
  },
})
```
