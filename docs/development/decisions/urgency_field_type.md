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

## Summary
The benefits of better query performance and natural ordering outweigh the reduced raw database readability, especially since we'll primarily interact through Django's ORM.

## Rationale
### IntegerField choice
1. Performance
   - Integer comparisons are more efficient for frequent querying
     Why: Database can compare numbers faster than text. Example: Finding all invoices with urgency > 3 is faster than comparing strings
   - Better database index performance
     Why: Integer indexes take less space and are faster to search. Example: Sorting 10,000 invoices by urgency is much quicker
   - Efficient storage space usage
     Why: Storing numbers (1-5) uses less space than strings ('CRITICAL'). Example: 1 byte vs 8 bytes per value

2. Natural ordering
   - Numeric values (1-5) naturally represent urgency levels
     Why: 1 is more urgent than 2 is more urgent than 3, just like in real life. Example: OVERDUE=1, CRITICAL=2 makes natural sense
   - Simplifies sorting and comparison operations
     Why: No need to map strings to numbers for comparison. Example: ORDER BY urgency DESC just works

### Null and blank configuration
1. `null=True` (Database level)
   - Allows NULL values in the database
     Why: We need a way to indicate "no value set". Example: When urgency hasn't been manually overridden
   - NULL indicates no manual override is set
     Why: Clear distinction between "not set" and "set to a value". Example: NULL means "use calculated urgency"
   - Lets urgency calculation fall back to due date
     Why: When no manual override exists, we calculate from the due date. Example: Invoice due tomorrow = HIGH urgency

2. `blank=True` (Form/validation level)
   - Allows the field to be empty in forms
     Why: Users need to be able to leave the field empty. Example: When creating a new invoice without setting urgency
   - Makes the manual override optional in UI
     Why: Not every invoice needs a manual urgency setting. Example: Most invoices use automatic calculation
   - Permits clearing of manual overrides
     Why: Users need to be able to remove manual settings. Example: When they want to go back to automatic calculation

## Alternatives considered
### CharField
- Pros:
  - Store urgency levels as strings ('OVERDUE', 'CRITICAL', etc.)
    Why: Values are human-readable in database. Example: SELECT * FROM invoices shows 'CRITICAL' instead of '2'
  - Direct mapping to enum names
    Why: No need to convert between numbers and names. Example: Code can use URGENCY.CRITICAL directly
  - More readable in raw database
    Why: Easier to understand data without looking up codes. Example: Database shows 'HIGH' instead of '3'

- Cons:
  - Larger storage footprint
    Why: Text takes more space than numbers. Example: 'CRITICAL' uses 8 bytes vs 1 byte for number 2
  - String comparisons for queries
    Why: Text comparisons are slower than number comparisons. Example: WHERE urgency < 'HIGH' is less efficient
  - No natural ordering
    Why: Text sorting might not match urgency levels. Example: 'HIGH' comes before 'LOW' alphabetically

### Custom field
- Pros:
  - Could encapsulate all urgency logic
    Why: Field handles all urgency-related rules. Example: Automatic validation and conversion in one place
  - Type safety at database level
    Why: Can't accidentally store invalid values. Example: Database ensures only valid urgency levels are saved

- Cons:
  - More complex implementation
    Why: Need to write and maintain custom field code. Example: Must handle serialization, validation, and migrations
  - Potential migration issues
    Why: Custom fields can be tricky to change later. Example: Changing urgency levels would need special migration code
  - Overkill for simple enumeration
    Why: Adds complexity for a simple numbered list. Example: IntegerField with choices is simpler and does the job

## Consequences
### Positive
- Better query performance
  Why: Integer operations are faster than string comparisons. Example: Finding all high-priority invoices (urgency <= 2) takes 50% less time than string matching
- Natural ordering for sorting
  Why: Numbers have inherent order matching urgency levels. Example: ORDER BY urgency ASC automatically sorts from most urgent (1) to least urgent (5)
- Efficient storage and indexing
  Why: Integer storage uses minimal space. Example: 1 million urgency values use 1MB vs 8MB for strings
- Clear null state handling
  Why: NULL clearly indicates no manual override. Example: System knows to use calculated urgency when manual_urgency IS NULL
- Flexible UI validation
  Why: blank=True lets forms handle empty values gracefully. Example: Users can clear manual urgency to return to automatic calculation

### Negative
- Less readable in raw database queries
  Why: Numbers need translation to understand meaning. Example: WHERE urgency = 2 is less clear than WHERE urgency = 'CRITICAL'
- Need to maintain mapping between numbers and urgency levels
  Why: Code must define and maintain number-to-name mapping. Example: URGENCY_CHOICES = [(1, 'OVERDUE'), (2, 'CRITICAL')] needs updating if levels change
- Less obvious meaning without context
  Why: Raw database values need documentation to understand. Example: New developer needs to look up what urgency=3 means

## Related decisions
- [Domain vs Django models](./domain_vs_django_models.md)