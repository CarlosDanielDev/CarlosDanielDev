# Controller Pattern (api)

This pattern is based on the controller implementation used in `api/src/controllers/`.

## Overview

Controllers in backend-service use:
- Class-based controllers extending `BaseController`
- Custom decorators for routes (`@Post`, `@Get`, etc.)
- Custom decorators for parameters (`@Body`, `@Param`, `@Query`)
- Dependency injection via constructor
- DTOs for request validation

## Directory Structure

```
src/controllers/
├── base.controller.ts           # Abstract base controller
├── interfaces/
│   └── icontroller.ts           # Controller interface
├── health.controller.ts         # Simple health check example
└── {domain}/
    ├── {domain}.controller.ts   # Domain controller
    └── dtos/
        └── {domain}.{action}.dto.ts  # Request/Response DTOs
```

## Base Controller (`base.controller.ts`)

```typescript
import ExpressBootstrap from '@infrastructure/express/express.bootstrap'
import IController from '@controllers/interfaces/icontroller'

export default abstract class BaseController implements IController {
  readonly basePath: string

  constructor(server: ExpressBootstrap, _basePath: string) {
    this.basePath = _basePath
    server.registerController(this)
  }
}
```

## Controller Pattern (`{domain}.controller.ts`)

```typescript
import { Body, Param, Query } from '@infrastructure/decorators/params.decorator'
import { Get, Post, Put, Delete } from '@infrastructure/decorators/routes.decorator'
import BaseController from '@controllers/base.controller'
import ExpressBootstrap from '@infrastructure/express/express.bootstrap'
import MyDomainService from '@services/{domain}/{domain}.service'
import CreateMyDomainDto from './dtos/{domain}.create.dto'
import UpdateMyDomainDto from './dtos/{domain}.update.dto'
import { logger } from '@infrastructure/log/logger.config'

export default class MyDomainController extends BaseController {
  readonly myDomainService!: MyDomainService

  constructor(server: ExpressBootstrap, myDomainService: MyDomainService) {
    super(server, '/{domain}')
    this.myDomainService = myDomainService
  }

  @Get('/', 'List all items')
  async list(@Query('aid') aid: string) {
    logger.info('GET /{domain}', { aid })
    return this.myDomainService.findAll(aid)
  }

  @Get('/:id', 'Get item by ID')
  async getById(@Param('id') id: string, @Query('aid') aid: string) {
    logger.info('GET /{domain}/:id', { id, aid })
    return this.myDomainService.findById(id, aid)
  }

  @Post('/', 'Create new item')
  async create(@Body() input: CreateMyDomainDto) {
    logger.info('POST /{domain}', {
      aid: input.aid,
      name: input.name,
    })
    return this.myDomainService.create(input)
  }

  @Put('/:id', 'Update item')
  async update(@Param('id') id: string, @Body() input: UpdateMyDomainDto) {
    logger.info('PUT /{domain}/:id', { id, aid: input.aid })
    return this.myDomainService.update(id, input)
  }

  @Delete('/:id', 'Delete item')
  async delete(@Param('id') id: string, @Query('aid') aid: string) {
    logger.info('DELETE /{domain}/:id', { id, aid })
    return this.myDomainService.delete(id, aid)
  }

  @Post('/bulk', 'Bulk operation')
  async bulkOperation(@Body() input: BulkOperationDto) {
    logger.info('POST /{domain}/bulk', {
      totalItems: input.items.length,
    })
    return this.myDomainService.bulkOperation(input)
  }
}
```

## Route Decorators

The custom decorators map to HTTP methods:

```typescript
// @infrastructure/decorators/routes.decorator.ts
@Get(path: string, description: string)    // HTTP GET
@Post(path: string, description: string)   // HTTP POST
@Put(path: string, description: string)    // HTTP PUT
@Delete(path: string, description: string) // HTTP DELETE
@Patch(path: string, description: string)  // HTTP PATCH
```

## Parameter Decorators

```typescript
// @infrastructure/decorators/params.decorator.ts
@Body()           // Request body (auto-validated with DTO)
@Param('name')    // URL parameter (/route/:name)
@Query('name')    // Query string parameter (?name=value)
@Headers('name')  // Request header
```

## Controller Registration

Controllers are registered in the application bootstrap:

```typescript
// src/index.ts or app bootstrap
const server = new ExpressBootstrap()

// Create services
const myDomainRepository = new MyDomainRepository(dbClient, traceService)
const myDomainService = new MyDomainService(myDomainRepository)

// Create and register controller
new MyDomainController(server, myDomainService)

// Start server
server.start()
```

## Key Rules

1. **Extend BaseController** - All controllers must extend `BaseController`
2. **Inject dependencies** - Services injected via constructor
3. **Use decorators** - Route and parameter decorators for clean API definition
4. **Log all requests** - Use logger at the start of each method
5. **Use DTOs** - Always validate input with DTO classes
6. **Return service results** - Controllers delegate to services
7. **Descriptive route comments** - Second parameter of route decorator is description
