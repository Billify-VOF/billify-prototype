# infrastructure/README.md

# Infrastructure Layer

The infrastructure layer implements technical details and interfaces defined by the domain layer.

## Structure

### Django
Framework-specific implementations:
- `models/` - Django ORM models
  - `cash_flow.py` - Cash flow data model
  - `invoice.py` - Invoice data model
- `repositories/` - Data access implementations
  - `cash_flow_repository.py` - Cash flow data access
  - `invoice_repository.py` - Invoice data access

### Storage
File and object storage implementations:
- `file_system.py` - Local file system operations
- `object_storage.py` - Cloud storage operations

## Guidelines

- Implement interfaces defined in domain layer
- Handle data persistence and retrieval
- Keep technical details isolated
- Framework-specific code belongs here