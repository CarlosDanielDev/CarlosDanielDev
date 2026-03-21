# Internationalization Patterns for mobile-app

i18n setup and translation patterns.

---

## i18n Setup

```javascript
// i18n/i18n.js
import I18n from 'react-native-i18n'
import en from './langs/en.js'
import pt_BR from './langs/pt_BR.js'
import es from './langs/es.js'

I18n.fallbacks = true
I18n.defaultLocale = 'en'
I18n.translations = {
  en,
  'pt-BR': pt_BR,
  es,
}

export default I18n
```

---

## Translation Files

### English (en.js)

```javascript
export default {
  common: {
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    confirm: 'Confirm',
    loading: 'Loading...',
  },
  products: {
    title: 'Products',
    add: 'Add Product',
    edit: 'Edit Product',
    name: 'Product Name',
    price: 'Price',
    description: 'Description',
  },
  errors: {
    required: 'This field is required',
    invalidEmail: 'Invalid email address',
    saveFailed: 'Failed to save',
  },
}
```

### Portuguese (pt_BR.js)

```javascript
export default {
  common: {
    save: 'Salvar',
    cancel: 'Cancelar',
    delete: 'Excluir',
    confirm: 'Confirmar',
    loading: 'Carregando...',
  },
  products: {
    title: 'Produtos',
    add: 'Adicionar Produto',
    edit: 'Editar Produto',
    name: 'Nome do Produto',
    price: 'Preço',
    description: 'Descrição',
  },
  errors: {
    required: 'Este campo é obrigatório',
    invalidEmail: 'E-mail inválido',
    saveFailed: 'Falha ao salvar',
  },
}
```

---

## Using Translations in Components

### Static Strings

```typescript
import I18n from '../../i18n/i18n'

const Strings = {
  t_title: I18n.t('products.title'),
  t_add: I18n.t('products.add'),
  t_name: I18n.t('products.name'),
  t_save: I18n.t('common.save'),
  t_cancel: I18n.t('common.cancel'),
}

const MyComponent = () => (
  <View>
    <Text>{Strings.t_title}</Text>
    <Button>{Strings.t_save}</Button>
  </View>
)
```

### Dynamic Translations

```typescript
// With interpolation
I18n.t('greeting', { name: 'John' })
// Translation: "Hello, {{name}}!" -> "Hello, John!"

// With count
I18n.t('items', { count: 5 })
// Translation with pluralization
```

---

## Translation with Variables

```javascript
// In translation file
export default {
  greeting: 'Hello, {{name}}!',
  itemCount: {
    zero: 'No items',
    one: '1 item',
    other: '{{count}} items',
  },
}

// Usage
I18n.t('greeting', { name: 'Maria' })
// Output: "Hello, Maria!"

I18n.t('itemCount', { count: 0 })  // "No items"
I18n.t('itemCount', { count: 1 })  // "1 item"
I18n.t('itemCount', { count: 5 })  // "5 items"
```

---

## Changing Language

```typescript
import I18n from '../../i18n/i18n'

const changeLanguage = (locale: string) => {
  I18n.locale = locale
  // Force re-render or restart app
}

// Usage
changeLanguage('pt-BR')
changeLanguage('en')
changeLanguage('es')
```

---

## Getting Current Language

```typescript
const currentLanguage = I18n.currentLocale()
// Returns: 'en', 'pt-BR', 'es', etc.
```

---

## Formatting Dates

```typescript
import I18n from '../../i18n/i18n'

const formatDate = (date: Date) => {
  return I18n.l('date.formats.default', date)
}

// Or use native formatting
const formatDate = (date: Date, locale: string) => {
  return new Intl.DateTimeFormat(locale).format(date)
}
```

---

## Formatting Currency

```typescript
const formatCurrency = (amount: number, currency: string = 'BRL') => {
  const locale = I18n.currentLocale()

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount)
}

// Usage
formatCurrency(1234.56, 'BRL') // "R$ 1.234,56" (pt-BR)
formatCurrency(1234.56, 'USD') // "$1,234.56" (en)
```

---

## Translation Keys Organization

```
common.*          - Shared strings (save, cancel, etc.)
errors.*          - Error messages
{feature}.*       - Feature-specific strings
  {feature}.title
  {feature}.description
  {feature}.actions.*
  {feature}.fields.*
```

---

## Best Practices

1. **Define strings early** - Create Strings object at component top
2. **Use namespaces** - Group related translations (products.*, orders.*)
3. **Avoid inline I18n.t()** - Pre-compute strings for performance
4. **Consistent keys** - Use same structure across languages
5. **Fallbacks** - Always provide en (English) as fallback
6. **Test all languages** - Verify layout with longer strings

---

## Example: Complete Component with i18n

```typescript
import React from 'react'
import { View } from 'react-native'
import { Container, Text, Button } from '@company/ui-components'
import { connect } from 'react-redux'
import I18n from '../../i18n/i18n'
import { generateTestID } from '../../util'

const Strings = {
  t_title: I18n.t('products.title'),
  t_description: I18n.t('products.description'),
  t_addButton: I18n.t('products.add'),
  t_empty: I18n.t('products.empty'),
  t_loading: I18n.t('common.loading'),
}

const ProductScreen: React.FC<Props> = ({
  products,
  loading,
  navigation,
}) => (
  <Container padding={20}>
    <Text {...generateTestID('title')}>{Strings.t_title}</Text>

    {loading ? (
      <Text>{Strings.t_loading}</Text>
    ) : products.length === 0 ? (
      <Text {...generateTestID('empty-state')}>{Strings.t_empty}</Text>
    ) : (
      <FlatList data={products} {...} />
    )}

    <Button
      {...generateTestID('add-button')}
      onPress={() => navigation.navigate('AddProduct')}
    >
      {Strings.t_addButton}
    </Button>
  </Container>
)

const mapStateToProps = (state: RootState) => ({
  products: state.products.list,
  loading: state.products.loading,
})

export default connect(mapStateToProps)(ProductScreen)
```
