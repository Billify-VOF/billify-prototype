# Domain modeling in Billify

## Overview
Domain modeling is the process of creating a conceptual model of the business domain. In Billify, this involves understanding and representing core business concepts in our code.

For implementation details, see:
- [Backend overview](../../../backend/backend-readme.md)
- [Domain layer](../../../backend/domain/README.md)
- [Infrastructure layer](../../../backend/infrastructure/README.md)
- [Domain vs Django models ADR](../decisions/domain_vs_django_models.md)

### Current implementation status

#### Implemented:
- Invoice domain model with:
  - Status tracking (pending, paid, overdue)
  - Urgency calculation based on due dates
  - Basic validation rules
  - Manual urgency override capability

#### Planned:
- Payment tracking and validation
- Cash flow forecasting and analysis
- Customer management
- Integration with:
  - Yuki (accounting data)
  - Ponto (banking data)

## Key domain model concepts

### Value objects
For detailed documentation of value objects, see [Value objects](./value_objects.md)

Example from our codebase ([value_objects.py](../../../backend/domain/models/value_objects.py)):
```python
class UrgencyLevel(Enum):
    """Value object representing invoice urgency with color codes."""
    OVERDUE = ("#8B0000", (None, -1))   # Dark red
    CRITICAL = ("#FF0000", (0, 7))      # Red
    HIGH = ("#FFA500", (8, 14))         # Orange
    MEDIUM = ("#FFD700", (15, 30))      # Yellow
    LOW = ("#008000", (31, None))       # Green

    @property
    def color_code(self) -> str:
        return self.value[0]

    @property
    def day_range(self) -> tuple[int | None, int | None]:
        return self.value[1]
```

### Entities
Example from our codebase ([Invoice](../../../backend/domain/models/invoice.py)):
```python
class Invoice:
    def __init__(
        self,
        amount: Decimal,
        due_date: date,
        invoice_number: str,
        file_path: str,
        invoice_id: Optional[int] = None
    ):
        self.id = invoice_id
        self.amount = amount
        self.due_date = due_date
        self.invoice_number = invoice_number
        self.file_path = file_path
        self.status = 'pending'
        self._manual_urgency = None

    def validate(self):
        """Apply business rules to validate invoice data."""
        if self.amount <= 0:
            raise InvalidInvoiceError("Invoice amount must be positive")

    @property
    def urgency(self) -> UrgencyLevel:
        if self._manual_urgency is not None:
            return self._manual_urgency
        days_until_due = (self.due_date - date.today()).days
        return UrgencyLevel.calculate_from_days(days_until_due)
```

### Key differences: entities vs value objects

1. **Identity Matters vs Value Matters**:
   - **Entities**: Two entities with identical data are still different entities
   ```python
     # Example: Two invoices for €100 to the same customer are different invoices
    invoice1 = Invoice(amount=100, due_date=date.today(), invoice_number="INV-001")
    invoice2 = Invoice(amount=100, due_date=date.today(), invoice_number="INV-002")
     # Even with same data, invoice1 ≠ invoice2 because they have different IDs
     ```
   - **Value Objects**: Two value objects with the same values are considered equal
     ```python
     # Example: Any reference to UrgencyLevel.HIGH is the same object
     urgency1 = UrgencyLevel.HIGH  # Orange, 8-14 days
     urgency2 = UrgencyLevel.HIGH  # Same object, same values
     assert urgency1 is urgency2  # True - they are the same object
    ```

2. **Mutability vs Immutability**:
   - **Entities**: Can be changed while remaining the same entity
    ```python
     # Example: An invoice's status can change, but it's still the same invoice
     invoice = Invoice(amount=100, due_date=date.today(), invoice_number="INV-001")
     invoice.status = 'pending'  # Initially pending
     # Later...
     invoice.status = 'paid'     # Status changed, but same invoice
    ```
   - **Value Objects**: Cannot be changed after creation
    ```python
     # Example: UrgencyLevel values are fixed
     urgency = UrgencyLevel.HIGH
     # Can't modify urgency.color_code or urgency.day_range
     # To use a different urgency, you must use a different enum value:
     new_urgency = UrgencyLevel.LOW
    ```

3. **Lifecycle vs State**:
   - **Entities**: Have a lifecycle that needs tracking
    ```python
     # Example: An invoice goes through various states
    invoice = Invoice(...)
     # We track its history:
     # 1. Created as pending
     assert invoice.status == 'pending'
     # 2. Marked as paid
     invoice.status = 'paid'
     # 3. Each state change is important for business logic
    ```
   - **Value Objects**: Represent a specific value at a point in time
    ```python
     # Example: UrgencyLevel just represents current urgency
     urgency = UrgencyLevel.calculate_from_days(10)  # HIGH
     # We don't track how it became HIGH
     # We don't care about its previous values
     # We only care about what it is right now
    ```

Why this matters in practice:
- When designing a new concept, ask:
  1. "Do we need to track its history?" → Probably an entity
  2. "Is it defined by its values?" → Probably a value object
  3. "Does it need a unique identity?" → Probably an entity
  4. "Can two instances with the same values be used interchangeably?" → Probably a value object

## Best practices

### 1. Type safety
Types help us prevent mistakes by making it impossible to use data in the wrong way. Think of it like having special containers for different things - you can't accidentally put soup in a fork or eat cereal with a plate.

Let's look at why primitive types (like strings) can be dangerous, and how proper types help:

Bad approach (using primitive types):
```python
class Invoice:
    def __init__(self, status: str):
        self.status = status  # Dangerous! Any string is allowed

    def mark_as_paid(self):
        # Problems with using strings:
        # 1. Typos won't be caught: 'payed' vs 'paid' or 'PAID' vs 'paid'
        # 2. Invalid states possible: 'dancing' is a valid string!
        # 3. No autocomplete - have to remember valid values
        self.status = 'paid'

# This code would work (but shouldn't!):
invoice = Invoice(status='dancing')  # Wrong but valid string
invoice.status = 'piad'  # Typo, but Python accepts it
```

Good approach (using proper types):
```python
from enum import Enum

class InvoiceStatus(Enum):
    PENDING = 'pending'
    PAID = 'paid'
    OVERDUE = 'overdue'

class Invoice:
    def __init__(self, status: InvoiceStatus):
        self.status = status  # Safe! Only valid statuses allowed

    def mark_as_paid(self):
        # Benefits of using InvoiceStatus:
        # 1. Only valid states possible
        # 2. Autocomplete shows all valid options
        # 3. Typos caught by IDE and Python
        self.status = InvoiceStatus.PAID

# Now this won't even run:
invoice = Invoice(status='dancing')  # Error! Must use InvoiceStatus
invoice.status = 'piad'  # Error! Must use InvoiceStatus.PAID
```

Real example from our codebase:
```python
# Instead of using strings for urgency levels:
urgency = 'high'  # Could be 'high', 'HIGH', 'High' - which is right?

# We use an Enum that makes it impossible to make mistakes:
class UrgencyLevel(Enum):
    OVERDUE = ("#8B0000", (None, -1))   # Dark red
    CRITICAL = ("#FF0000", (0, 7))      # Red
    HIGH = ("#FFA500", (8, 14))         # Orange
    MEDIUM = ("#FFD700", (15, 30))      # Yellow
    LOW = ("#008000", (31, None))       # Green

# Now we get:
# 1. Autocomplete: UrgencyLevel.HI<press tab> completes to HIGH
# 2. Error checking: UrgencyLevel.MEDIUM_HIGH would be an error
# 3. Built-in behavior: color_code and day_range are always correct
```

Why this matters:
1. **Catch mistakes early**:
   - IDE warns you immediately about wrong values
   - No need to run the code to find typos
   - Can't accidentally use invalid values

2. **Self-documenting code**:
   - The type tells you exactly what values are allowed
   - No need to check documentation for valid states
   - Autocomplete shows you all valid options

3. **Refactoring safety**:
   - If you rename a status, the IDE updates all uses
   - If you add a new status, you'll find all places that need updating
   - If you remove a status, you'll find all places that need fixing

4. **Better than comments**:
   ```python
   # Bad: comment tells you what's allowed
   status: str  # Can be 'pending', 'paid', or 'overdue'

   # Good: type enforces what's allowed
   status: InvoiceStatus  # Only valid values possible
   ```

Remember: types are like guardrails - they keep you from accidentally driving off the road. They're not about checking if you're following the speed limit (that's validation's job).

### 2. Validation
While type safety prevents incorrect types, validation enforces business rules within those types. It's about ensuring the data makes sense for our business.

Different types of validation in our codebase:

1. **Domain rules**:
  ```python
  def validate(self):
      """Apply business rules to validate invoice data."""
      if self.amount <= 0:
          raise InvalidInvoiceError("Invoice amount must be positive")
        
        # Future validation rules can be added here:
        # if self.due_date < date.today():
        #     raise InvalidInvoiceError("Due date cannot be in the past")
  ```
  - Ensures business rules are followed
  - Provides clear error messages about what's wrong
  - Centralized in the domain object that owns the rules

2. **Range/boundary validation**:
   ```python
   @classmethod
   def calculate_from_days(cls, days: int) -> 'UrgencyLevel':
       """Calculate urgency level from days until due."""
       if days < 0:
           return cls.OVERDUE
       if 0 <= days <= 7:
           return cls.CRITICAL
       # ... other ranges ...
       raise ValueError(f"Invalid days value: {days}")
   ```
   - Ensures values are within acceptable ranges
   - Maps values to appropriate business concepts
   - Fails early if values don't make sense

3. **State transition validation**:
  ```python
  def mark_as_paid(self):
      """Mark invoice as paid if in valid state."""
      if self.status not in ['pending', 'overdue']:
          raise InvalidStateTransition(
              f"Cannot mark as paid from status: {self.status}"
          )
      self.status = 'paid'
  ```
   - Ensures objects only change state in valid ways
   - Prevents impossible state transitions
   - Makes business rules explicit in code

### 3. Rich domain models
Instead of having "dumb" data containers, we create "smart" objects that know how to work with their own data and enforce their own rules.

Bad approach (anemic domain model):
```python
# Just stores data without behavior
class Invoice:
    def __init__(self, amount: Decimal, due_date: date):
        self.amount = amount
        self.due_date = due_date
        self.status = 'pending'

# Business logic lives elsewhere
def calculate_invoice_urgency(invoice):
    days = (invoice.due_date - date.today()).days
    if days < 0:
        return 'OVERDUE'
    # ... etc
```

Good approach (our rich domain model):
```python
class Invoice:
    def __init__(self, amount: Decimal, due_date: date, ...):
        self.amount = amount
        self.due_date = due_date
        self.status = 'pending'
        self._manual_urgency = None
        # Validates itself on creation
        self.validate()

    def validate(self):
        """Knows its own rules"""
        if self.amount <= 0:
            raise InvalidInvoiceError("Invoice amount must be positive")

    @property
    def urgency(self) -> UrgencyLevel:
        """Knows how to calculate its own urgency"""
        if self._manual_urgency is not None:
            return self._manual_urgency
        days_until_due = (self.due_date - date.today()).days
        return UrgencyLevel.calculate_from_days(days_until_due)

    def mark_as_paid(self):
        """Knows how to handle its own state changes"""
        if self.status not in ['pending', 'overdue']:
            raise InvalidStateTransition(
                f"Cannot mark as paid from status: {self.status}"
            )
        self.status = 'paid'
```

Benefits of rich domain models:
1. **Self-contained**: The object knows how to:
   - Validate its own data
   - Calculate its own derived values
   - Manage its own state changes

2. **Protected rules**: Can't accidentally break business rules because:
   - The object validates itself when created
   - State changes are controlled through methods
   - Complex calculations are encapsulated

3. **Clear usage**: Other code doesn't need to know implementation details:
  ```python
  # Simple to use because Invoice knows what to do
  invoice = Invoice(amount=Decimal("100.00"), due_date=date.today(), invoice_number="INV-001")
   
  # Don't need to know how urgency is calculated
  print(invoice.urgency)  # Just works!
   
  # Don't need to know valid state transitions
  invoice.mark_as_paid()  # Handles all validation internally
   
  # Don't need to know about manual urgency override implementation
  invoice.set_urgency_manually(UrgencyLevel.HIGH)  # Encapsulates the details
  ```

This makes the code:
- Easier to use correctly (the API guides you)
- Harder to use incorrectly (invalid operations are prevented)
- More maintainable (implementation details can change without affecting users)
- Self-documenting (methods tell you what they do)