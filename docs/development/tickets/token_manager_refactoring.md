# Refactoring Ticket: Token Manager Module

## Title
Refactor `token_manager` Module to Follow DDD Principles

## Description
The current `token_manager` module doesn't align with our DDD architectural principles. It mixes business logic, persistence, and API concerns, and directly accesses the database without using the repository pattern.

## Background
- The `token_manager` module handles Ponto API integration and token management
- Currently, it includes both domain logic (token encryption/decryption) and infrastructure concerns (database storage)
- It works but violates our architectural principles, making it harder to test, maintain, and extend

## Requirements

### 1. Create Domain Models
- Create `domain/models/integrations/ponto_token.py` with pure Python domain models
- Define value objects for tokens, encryption keys, etc.
- Move validation logic to domain models

### 2. Create Domain Services
- Create `domain/services/integrations/ponto_service.py` for business logic
- Move authentication flow logic from views to the service
- Implement token refresh business rules in the service

### 3. Define Repository Interfaces
- Create `domain/repositories/interfaces/ponto_token_repository.py`
- Define clear methods for saving and retrieving tokens
- Include proper type hints and documentation

### 4. Implement Infrastructure Layer
- Create `infrastructure/django/models/ponto_token.py` for Django ORM model
- Implement `infrastructure/django/repositories/ponto_token_repository.py`
- Add proper conversion between domain and Django models

### 5. Update API Layer
- Move HTTP-specific code to `api/views/integrations/ponto.py`
- Update views to use domain services instead of direct model access
- Ensure proper error handling and serialization

### 6. Update Tests
- Create unit tests for domain models and services
- Create integration tests for repositories
- Update any existing tests to work with the new structure

### 7. Migration Plan
- Create a migration script to transfer existing data
- Ensure backward compatibility during transition
- Update any references to the old module

## Technical Guidelines
- Follow the repository pattern as described in `docs/development/decisions/domain_vs_django_models.md`
- Use dependency injection for repositories
- Properly handle exceptions using domain-specific exceptions
- Document all public interfaces thoroughly

## Acceptance Criteria
- [ ] All functionality works as before
- [ ] Code follows DDD architecture
- [ ] All tests pass
- [ ] No direct database access in domain or API layers
- [ ] Clean separation of business logic and infrastructure concerns
- [ ] Documentation is updated to reflect new structure

## Estimated Effort
Medium (3-5 days)

## Priority
High - This establishes a pattern for future refactoring 