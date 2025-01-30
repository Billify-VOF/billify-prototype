# Domain layer

The domain layer contains the core business logic and rules of our application. It is completely independent of frameworks and technical implementations, following Domain-Driven Design principles.

## Structure

### Models (`models/`)
Pure business objects representing core concepts:
- `invoice.py` - Invoice entity with validation rules and business logic
- `cash_flow.py` - Cash flow calculations and projections (planned)
- `value_objects.py` - Immutable value objects for business concepts

### Services (`services/`)
Business operations and workflows:
- `invoice_service.py` - Invoice processing and validation
- `cash_flow_service.py` - Cash flow analysis (planned)

### Repositories (`repositories/`)
Interfaces for data persistence:
- `interfaces/` - Abstract base classes defining repository contracts
  - `invoice_repository.py` - Invoice data access interface
  - `cash_flow_repository.py` - Cash flow data access interface (planned)

### Exceptions (`exceptions.py`)
Domain-specific exceptions:
- `InvoiceError` - Invoice-related business rule violations
- `ValidationError` - Domain validation failures
- `RepositoryError` - Data access issues

## Domain rules

### Invoice processing
- Validation rules for invoice data
- Business rules for invoice states
- Processing workflow requirements

### Cash flow (planned)
- Cash flow calculation rules
- Projection and analysis logic
- Financial reporting requirements

## Guidelines

### Code organization
- Keep business logic isolated from infrastructure
- Use pure Python classes and type hints
- Define clear interfaces for technical implementations
- Maintain separation of concerns

### Domain model design
- Use rich domain models with behavior
- Implement value objects for immutable concepts
- Keep entities focused and cohesive
- Follow Single Responsibility Principle

### Error handling
- Use domain-specific exceptions
- Validate business rules at the domain level
- Maintain clear error messages
- Handle edge cases explicitly

### Testing
- Unit test all business rules
- Use test-driven development (TDD)
- Mock external dependencies
- Focus on behavior, not implementation

## Best practices

1. **Dependency rule**: Domain layer should not depend on outer layers
2. **Immutability**: Use immutable objects where possible
3. **Validation**: Enforce invariants at object creation
4. **Encapsulation**: Hide implementation details
5. **Documentation**: Document business rules and decisions