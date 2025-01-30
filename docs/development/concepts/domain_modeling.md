# Domain modeling in Billify

## Overview
Domain modeling is the process of creating a conceptual model of the business domain. In Billify, this involves understanding and representing core business concepts like invoices, payments, and financial data in our code.

This document contains both implemented examples from our codebase (with links to source) and theoretical examples for illustration.

## Key domain model concepts

### Value objects
See detailed documentation in [value_objects.md](./value_objects.md)
> Implementation examples: [backend/domain/models/value_objects.py](../../../backend/domain/models/value_objects.py)

Key points:
- Objects defined by their values rather than identity
- Immutable after creation
- Used for concepts where identity doesn't matter
- Examples in Billify: 
  - Implemented: urgencyLevel
  - Planned: money (not yet implemented)

### Entities
> Implementation example: [backend/domain/models/invoice.py](../../../backend/domain/models/invoice.py)

Objects that have a distinct identity that runs through time and different representations:
- Have a unique identifier
- Can be changed while remaining the same entity
- Example: an invoice remains the same entity even when its status changes (implemented)

### Aggregates
Clusters of domain objects that can be treated as a single unit:
- Have a root entity
- Ensure consistency boundaries
- Example: an invoice (root) with its line items and payment records (partially implemented)

### Domain services
Operations that don't naturally belong to any entity or value object:
- Represent domain concepts that are actions rather than things
- Often involve multiple domain objects
- Example: invoice payment processing service (planned)

## Best practices in domain modeling

### 1. Focus on business language
- Use ubiquitous language from the business domain
- Avoid technical terms where business terms exist
- Example: use "overdue" instead of "payment_status_negative"

### 2. Encapsulation
- Hide implementation details
- Expose only what's necessary
- Protect invariants

### 3. Immutability
- Make value objects immutable
- Create new instances instead of modifying existing ones
- Helps prevent bugs and makes code easier to reason about

### 4. Type safety
- Use type hints
- Create specific types for domain concepts
- Avoid primitive obsession

### 5. Validation
- Validate at object creation
- Ensure business rules are enforced
- Raise domain-specific exceptions

## Common patterns in Billify

### Factory methods
Used when object creation involves logic:
> Example from UrgencyLevel in [backend/domain/models/value_objects.py](../../../backend/domain/models/value_objects.py) (implemented)

```python
@classmethod
def calculate_from_days(cls, days: int) -> 'UrgencyLevel':
    if days < 0:
        raise ValueError("Days cannot be negative")
    # ... logic to determine urgency level
```

### Rich domain models
- Behavior and data together
- Business rules encoded in domain objects
- Avoid anemic domain models

### Separation of concerns
- Domain logic separate from infrastructure
- Clear boundaries between layers
- Domain model independent of persistence 