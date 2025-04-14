# Value objects in Billify

## Overview
Value objects are a fundamental concept in domain-driven design (DDD) where objects are defined by their values rather than their identity. They are immutable after creation and two value objects with the same values are considered equal.

## Key characteristics
- Defined by their values, not identity
- Immutable after creation
- Two objects with the same values are considered equal
- New instances are created rather than modifying existing ones

## Examples in Billify

The following examples demonstrate value objects in Billify. Some are actual implementations from our codebase (with links to the source), while others are theoretical examples used for illustration.

### Money value object (theoretical example)
This is a theoretical example to illustrate value objects. The Money class is not yet implemented in Billify but demonstrates the concept well.

```python
amount1 = Money(100, "EUR")
amount2 = Money(100, "EUR")
```
Key points:
- We don't care about which specific money object it is
- We only care about the total amount and currency
- Two money objects with 100 EUR are considered equal
- We create new money objects rather than modifying existing ones

### Urgency level value object (implemented)
> Implementation: [backend/domain/models/value_objects.py](../../../backend/domain/models/value_objects.py)

```python
urgency1 = UrgencyLevel.HIGH
urgency2 = UrgencyLevel.HIGH
```
Key points:
- Defined by its level/value (overdue, critical, high, etc.)
- Two "high" urgency levels are identical
- No need to track the identity of urgency levels

## Understanding identity vs value objects

### Objects with identity (entities)
> Implementation: [backend/domain/models/invoice.py](../../../backend/domain/models/invoice.py)

Example using an invoice (implemented):
```python
invoice1 = Invoice(total_amount=100, invoice_number="INV-001", due_date=...)
invoice2 = Invoice(total_amount=100, invoice_number="INV-001", due_date=...)
```
Even with identical properties, these are different because each invoice has:
- Unique ID in the database
- Its own lifecycle (created, paid, overdue)
- History of changes
- Distinct business meaning

### Objects without identity (value objects)
Theoretical example using money (not yet implemented):
```python
amount1 = Money(100, "EUR")
amount2 = Money(100, "EUR")
```
These are considered the same because:
- €100 is €100, regardless of which instance represents it
- No need to track "which" €100 it is
- They're interchangeable
- No unique ID or lifecycle

## Best practices
1. Always make value objects immutable
   Why: Prevents bugs from unexpected state changes. Example: Our UrgencyLevel can't be modified after creation, ensuring consistent behavior

2. Implement value-based equality
   Why: Two value objects with same data should be equal. Example: Two UrgencyLevel(2) objects are equal regardless of when they were created

3. Use factory methods for complex creation logic
   Why: Special class methods that create objects, hiding complex initialization logic. Example: Instead of calculating urgency directly:
   ```python
   # Without factory method - complex logic exposed:
   days_until_due = (due_date - today).days
   urgency = UrgencyLevel(2 if days_until_due <= 7 else 3)

   # With factory method - logic hidden and reusable:
   urgency = UrgencyLevel.from_due_date(due_date)
   ```

4. Consider using value objects for concepts that don't need identity
   Why: Simpler than full entities when identity isn't important. Example: An invoice's urgency level doesn't need its own ID

5. Document the rationale for choosing between entities and value objects
   Why: Makes design decisions clear for the team. Example: We document why Invoice is an entity but UrgencyLevel is a value object 