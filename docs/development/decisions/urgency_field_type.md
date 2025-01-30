# Adr: Using IntegerField for urgency storage

## Status
Accepted

## Context
When implementing invoice urgency levels in our Django model, we needed to decide how to store the urgency values in the database. The urgency levels (OVERDUE, CRITICAL, HIGH, MEDIUM, LOW) needed to be efficiently stored and queried while maintaining data integrity.

## Decision
We decided to use `IntegerField` for storing urgency levels in the database, with numeric values mapping to urgency levels (e.g., 1=OVERDUE, 2=CRITICAL, etc.).

For the manual urgency override field, we configured it with both `null=True` and `blank=True`:
```python
manual_urgency = models.IntegerField(null=True, blank=True)
```

## Rationale
### IntegerField choice
1. Performance
   - Integer comparisons are more efficient for frequent querying
   - Better database index performance
   - Efficient storage space usage

2. Natural ordering
   - Numeric values (1-5) naturally represent urgency levels
   - Simplifies sorting and comparison operations

### Null and blank configuration
1. `null=True` (Database level)
   - Allows NULL values in the database
   - NULL indicates no manual override is set
   - Lets urgency calculation fall back to due date

2. `blank=True` (Form/validation level)
   - Allows the field to be empty in forms
   - Makes the manual override optional in UI
   - Permits clearing of manual overrides

## Alternatives considered
### CharField
- Pros:
  - Store urgency levels as strings ('OVERDUE', 'CRITICAL', etc.)
  - Direct mapping to enum names
  - More readable in raw database
- Cons:
  - Larger storage footprint
  - String comparisons for queries
  - No natural ordering

### Custom field
- Pros:
  - Could encapsulate all urgency logic
  - Type safety at database level
- Cons:
  - More complex implementation
  - Potential migration issues
  - Overkill for simple enumeration

## Consequences
### Positive
- Better query performance
- Natural ordering for sorting
- Efficient storage and indexing
- Clear null state handling
- Flexible UI validation

### Negative
- Less readable in raw database queries
- Need to maintain mapping between numbers and urgency levels
- Less obvious meaning without context

## Related decisions
- [Domain vs Django models](./domain_vs_django_models.md)

## Notes
The benefits of better query performance and natural ordering outweigh the reduced raw database readability, especially since we'll primarily interact through Django's ORM. 