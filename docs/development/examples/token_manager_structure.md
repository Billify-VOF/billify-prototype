# Token Manager Refactoring: Directory Structure

This document outlines the proposed directory structure for the refactored token_manager module to follow Domain-Driven Design principles.

## Current Structure (Non-Compliant)

```
backend/
└── token_manager/
    ├── views.py             # Contains both business logic and API endpoints
    ├── models.py            # Django ORM models directly used in business logic
    ├── serializers.py       # API serialization
    └── management/
        └── commands/        # Management commands
```

## Proposed Structure (DDD-Compliant)

```
backend/
├── domain/
│   ├── models/
│   │   └── integrations/
│   │       └── ponto_token.py       # Domain entities and value objects
│   ├── services/
│   │   └── integrations/
│   │       └── ponto_service.py     # Business logic for token management
│   └── repositories/
│       └── interfaces/
│           └── ponto_token_repository.py  # Repository interface
│
├── infrastructure/
│   └── django/
│       ├── models/
│       │   └── integrations/
│       │       └── ponto_token.py   # Django ORM model
│       └── repositories/
│           └── integrations/
│               └── ponto_token_repository.py  # Repository implementation
│
├── api/
│   ├── views/
│   │   └── integrations/
│   │       └── ponto.py    # API endpoints
│   └── serializers/
│       └── integrations/
│           └── ponto.py    # Data serialization
│
└── application/
    └── management/
        └── commands/
            └── integrations/
                └── refresh_ponto_tokens.py  # Management commands
```

## Key Differences

1. **Separation of Concerns**:
   - Domain models contain only business logic and validation
   - Infrastructure layer handles persistence details
   - API layer focuses on HTTP protocol concerns
   - Application layer contains management commands

2. **Repository Pattern**:
   - Domain defines interface through repositories
   - Infrastructure implements concrete repositories
   - No direct model access in business logic

3. **Dependency Direction**:
   - Domain layer has no dependencies on outer layers
   - Infrastructure depends on domain interfaces
   - API depends on domain services

4. **Organization by Domain Context**:
   - All Ponto-related components grouped under 'integrations'
   - Clear boundaries between different integration types

## Implementation Strategy

1. Create the new structure while keeping the old one
2. Gradually migrate functionality to the new structure
3. Update references to use the new components
4. Remove the old structure once migration is complete

This approach allows for incremental migration without breaking existing functionality. 