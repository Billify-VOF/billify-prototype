# DDD Compliance Issues

This document outlines the areas of the codebase that don't align with our Domain-Driven Design (DDD) architectural principles as defined in `backend/backend-readme.md` and other architectural documentation.

## Non-Compliant Modules

### 1. `backend/token_manager/`

**Current Implementation:**
- Directly contains views, models, and business logic
- Uses Django models for business logic
- No separation between domain and infrastructure concerns
- No repository pattern implementation

**DDD-Compliant Structure Should Be:**
- Domain models in `domain/models/`
- Domain services in `domain/services/`
- Repository interfaces in `domain/repositories/interfaces/`
- Django-specific implementation in `infrastructure/django/models/` and `infrastructure/django/repositories/`
- API endpoints in `api/views/`

### 2. `backend/apps/`

**Current Implementation:**
- Traditional Django app structure (models, views, etc. in a single package)
- Business logic mixed with persistence concerns
- Direct database access in views and services

**DDD-Compliant Structure Should Be:**
- Move models to domain layer (business logic) and infrastructure layer (persistence)
- Move services to domain layer
- Implement repository pattern for data access
- Keep only configuration (admin.py, apps.py) at app level

### 3. `backend/billify/`

**Current Implementation:**
- Traditional Django project structure
- Contains URL routing and WSGI/ASGI configuration

**DDD-Compliant Structure Should Be:**
- Move URL routing to `api/urls.py`
- Move WSGI/ASGI configuration to `config/` package

### 4. `backend/utils/`

**Current Implementation:**
- Generic utility functions without clear domain context
- Used across different layers

**DDD-Compliant Structure Should Be:**
- Move utilities to domain services or infrastructure services based on their purpose
- Organize utilities by domain context, not as a separate module

## Refactoring Strategy

The refactoring strategy will be implemented in phases:

### Phase 1: Document and Plan
- Create tickets for each non-compliant module
- Establish clear migration paths
- Define target architecture

### Phase 2: Implement Repositories
- Create domain repositories for each entity
- Implement Django-specific repositories in infrastructure layer
- Update service code to use repositories instead of direct model access

### Phase 3: Separate Domain and Infrastructure
- Move business logic to domain layer
- Move persistence concerns to infrastructure layer
- Create clean interfaces between layers

### Phase 4: Reorganize API Layer
- Update API views to use domain services
- Remove direct model access from views
- Ensure proper error handling and conversion between layers

## Impact on Existing Code

The refactoring will:
- Improve maintainability by separating concerns
- Make testing easier by allowing domain logic to be tested independently
- Facilitate future changes by isolating technical implementations
- Ensure consistent architectural patterns across the codebase

However, it will require careful coordination to avoid breaking existing functionality during the transition. 