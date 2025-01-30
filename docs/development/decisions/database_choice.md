# Adr: Choosing PostgreSQL over MongoDB for MVP

## Status
Accepted

## Context
During MVP planning, we considered whether to use MongoDB instead of PostgreSQL, with the key question being whether MongoDB would enable faster implementation and deployment.

Our MVP requirements show we need to handle:
- 10-100 users initially
- ~7,200 read operations per day (0.083 reads/second)
- ~14,400 write operations per day (0.167 writes/second)
- ~300MB storage per user per month
- Complex financial calculations and data relationships

## Decision
We decided to use PostgreSQL with Django's ORM for the MVP phase instead of MongoDB.

Example of the simplicity with PostgreSQL and Django:
```python
# PostgreSQL with Django - Everything works out of the box
class CashFlowPosition(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2)
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    # Django automatically handles:
    # - Database migrations
    # - Admin interface
    # - Form handling
    # - Validation
    # - Serialization
```

Compared to MongoDB equivalent:
```python
# MongoDB - Requires additional setup and configuration
from mongoengine import Document, DecimalField, ReferenceField
from bson import Decimal128

class CashFlowPosition(Document):
    user = ReferenceField(User, required=True)
    current_balance = DecimalField(precision=2, required=True)
    calculated_at = DateTimeField(default=datetime.utcnow)
    
    # Need to manually handle:
    # - Schema changes
    # - Admin interface setup
    # - Custom serialization for Decimal128
    # - Custom validation
```

## Rationale

### Data structure and relationships
- Clear relational patterns between entities (Users, Invoices, Transactions)
- Many crucial foreign key relationships
- Financial data requires ACID compliance
- Complex joins needed for financial calculations

### Integration requirements
- Integration with Yuki and Ponto providing structured financial data
- Transformations fit naturally into a relational model
- VAT calculations require reliable joins and aggregations

### Development speed advantages
- Django's ORM optimized for PostgreSQL
- Team's existing experience with relational databases
- Built-in features ready to use
- Simpler implementation of financial calculations

### MVP scale considerations
- PostgreSQL easily handles our projected scale
- No optimization needed for initial user base
- Storage needs well within capabilities

### Future scalability options
- Can improve through proper indexing
- Connection pooling available
- Read replicas possible
- Can support up to 175 users before significant changes needed

## Alternatives considered

### MongoDB
Pros:
- Schema flexibility
- Potentially simpler for document-style data
- Good for rapid prototyping

Cons:
- More complex for financial calculations
- Manual handling of transactions needed
- Additional setup for decimal handling
- Less suitable for relational data
- Team would need to learn new patterns

## Consequences

### Positive
- Faster MVP development with Django's built-in features
- Better handling of financial calculations
- Strong data integrity guarantees
- Simpler backup and recovery
- Built-in support for complex queries
- Excellent support for time-series data

### Negative
- Less schema flexibility
- Might need migrations for schema changes
- Vertical scaling may be needed eventually

## Related decisions
- [Domain vs Django models](./domain_vs_django_models.md)

## Notes
While MongoDB offers schema flexibility, our MVP requirements show we have well-defined data structures and need strong data consistency, complex joins for financial calculations, and robust transaction support. PostgreSQL with Django provides the right balance of development speed, data integrity, and scalability for our specific use case. 