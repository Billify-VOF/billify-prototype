# domain/README.md

# Domain Layer

The domain layer contains the core business logic and rules of our application. It is completely independent of frameworks and technical implementations.

## Structure

### Models
Pure business objects representing core concepts:
- `cash_flow.py` - Cash flow business rules and calculations
- `invoice.py` - Invoice business rules and validation
- `value_objects.py` - Shared business value objects

### Services
Business operations and workflows:
- `cash_flow_service.py` - Cash flow operations
- `invoice_service.py` - Invoice processing logic

### Repositories
Interfaces for data access:
- `interfaces/`
  - `cash_flow_repository.py` - Cash flow data access interface
  - `invoice_repository.py` - Invoice data access interface

## Guidelines

- No framework dependencies allowed
- Use pure Python classes
- Define interfaces for technical implementations
- Keep business rules isolated and clear