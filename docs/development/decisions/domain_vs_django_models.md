# Adr: Separating domain and infrastructure models

## Status
Accepted

## Context
In developing Billify's invoice management system, we needed to decide how to structure our models. The key question was whether to combine business logic and persistence in Django models or separate them into distinct domain and infrastructure layers.

## Decision
We decided to maintain two separate models:
1. Domain model (`domain/models/invoice.py`): Business logic and rules
2. Django model (`infrastructure/django/models/invoice.py`): Data persistence

We're using the repository pattern to bridge these models:
```python
class InvoiceRepository:
    def save(self, domain_invoice: DomainInvoice):
        django_invoice = self._to_django(domain_invoice)
        django_invoice.save()
    
    def get(self, invoice_id) -> DomainInvoice:
        django_invoice = DjangoInvoice.objects.get(id=invoice_id)
        return self._to_domain(django_invoice)
```

## Rationale
1. Clean separation of concerns
   - Domain model focuses purely on business rules
   - Infrastructure model handles only persistence
   - No mixing of storage details with business logic

2. Flexibility and maintainability
   - Can change database without affecting business logic
   - Can modify business rules without touching persistence
   - Easier to test business logic in isolation
   - Clearer code organization

3. Business focus
   - Domain model speaks business language
   - Business rules are explicit and centralized
   - Easier for new developers to understand business requirements

## Understanding the layers

### Domain layer
- Represents our business domain (invoice management, cash flow, etc.)
- Contains core business concepts, rules, and logic
- Uses business language that stakeholders understand
- Example: Concepts like "invoice urgency" and "due date" are domain concepts

### Infrastructure layer
- Provides technical infrastructure to support the domain
- Handles technical concerns like:
  - Database storage (Django models)
  - External API communications (Yuki, Ponto)
  - File systems
  - Email services
- Example: How we store an invoice in PostgreSQL is an infrastructure concern

## Understanding persistence
Persistence refers to the ability of data to survive beyond the execution of the program that created it. Our infrastructure model handles:

1. Database operations
   - Saving data to the database
   - Loading data from the database
   - Managing database transactions
   - Handling database queries

2. Database schema management
   - Defining table structures
   - Specifying field types and constraints
   - Setting up indexes for performance
   - Managing relationships between tables

Example infrastructure model:
```python
class InvoiceModel(models.Model):
    # Defines how each piece of data is stored in the database
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    manual_urgency = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'invoices'
        indexes = [...]  # Database optimizations
```

## Additional benefits

### Technology independence
- Business logic remains independent of storage technology
- Can switch databases without changing domain code
- Multiple implementations can coexist (e.g., cached, audited versions)

### Testability
- Easy to create mock implementations for testing
- Can test business logic without a real database
- Simplified unit testing setup

### Team collaboration
- Teams can work on different implementations simultaneously
- Clear boundaries between domain and infrastructure code
- Reduced merge conflicts and dependencies between teams

## Practical applications

### Database migration
```python
# Can easily switch implementations
repository = DjangoInvoiceRepository()  # PostgreSQL
repository = MongoInvoiceRepository()   # MongoDB
```

### Testing
```python
# Simple mock for testing
class MockInvoiceRepository(InvoiceRepository):
    def save(self, invoice: Invoice, user_id: int) -> Invoice:
        return invoice
```

### Feature addition
```python
# Can add new implementations without changing existing code
class CachedInvoiceRepository(InvoiceRepository):
    # Adds caching layer
    pass
```

## Best practices
1. Keep interfaces focused on business operations
2. Implement conversion logic in repository implementations
3. Use dependency injection for flexibility
4. Keep domain models clean of infrastructure concerns

## Alternatives considered
1. Single Django model
   - Pros: Simpler, less code
   - Cons: Mixes business and storage concerns
   
2. Active record pattern
   - Pros: More straightforward
   - Cons: Tighter coupling, harder to change

3. Pure domain model
   - Pros: Clean business logic
   - Cons: More complex persistence

## Consequences
### Positive
- Clear separation between business logic and persistence
- Easier to test business rules in isolation
- More flexible for future changes
- Better organization of code
- Follows domain-driven design principles

### Negative
- More initial code to write
- Need to maintain two models
- More complex architecture
- Need for mapping between domain and infrastructure models

## Related decisions
- [Urgency field type](./urgency_field_type.md)

## Notes
The benefits of clean separation, flexibility, and maintainability outweigh the additional complexity, especially as the application grows and business rules become more complex. 