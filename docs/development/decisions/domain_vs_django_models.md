# Adr: Separating domain and infrastructure models

## Status
Accepted

## Context
Decision to make: Combine business logic and persistence in Django models or separate them into distinct domain and infrastructure layers.

## Decision made
We decided to maintain two separate models:
1. Domain model (`domain/models/invoice.py`): Business logic and rules
2. Django model (`infrastructure/django/models/invoice.py`): Data persistence

We're using the repository pattern (see [Understanding the Repository Pattern](#understanding-the-repository-pattern)) to bridge these models.

## Key Principles
Throughout this decision and its implementation, we follow these core principles:
1. Keep interfaces focused on business operations
2. Implement conversion logic in repository implementations
3. Keep domain models clean of infrastructure concerns

## Benefits and Rationale

Our approach provides several key benefits:

1. **Clean Separation of Concerns**
   - Domain model focuses purely on business rules
   - Infrastructure model handles only persistence (see [Understanding persistence](#understanding-persistence))
   - No mixing of storage details with business logic
   - Storage details isolated in repository implementation

2. **Flexibility and Maintainability**
   - Can change database without affecting business logic (see [Technology independence](#technology-independence))
   - Can modify business rules without touching persistence (database)
   - Support for multiple data sources behind same interface 
   - Future changes require minimal code modifications 
   - Multiple implementations can coexist (e.g., cached, audited versions)

3. **Enhanced Testing**
   - Comprehensive testing benefits detailed in [Understanding Simplified Unit Testing Setup](#understanding-simplified-unit-testing-setup)
   - Enables clean separation of business logic testing from infrastructure (see [Understanding the layers](#understanding-the-layers))

4. **Business Focus**
   - Domain model speaks business language
   - Business rules are explicit and centralized
   - Easier for new developers to understand requirements

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

We separate our models into two distinct responsibilities:

1. Domain Model: Handles business rules (like calculating invoice urgency)
2. Django Model: Handles persistence (database operations)

Key differences:
- Domain model focuses on behavior and business rules
- Django model focuses on storage and database structure
- No business logic in the Django model
- No database concerns in the domain model

## Understanding the Repository Pattern

In Billify, we use the Repository Pattern to bridge between our domain models and database storage. 

### What is the Repository Pattern?
The Repository Pattern acts as a translator between two parts of our system:
1. Business Logic: The code that handles business rules (like calculating invoice urgency)
2. Data Storage: The code that saves and loads data from the database

It provides simple methods like `get()` and `save()` that hide the complex database operations. This means:
- Business code can focus on business rules without worrying about database details
- All database access code is organized in one place
- We can change how we store data without changing our business code
- We can easily add features like caching or logging without affecting other code

### Implementation
The repository pattern is implemented through various repository classes, each serving a specific purpose:

```python
# Base Repository (Interface)
class InvoiceRepository(ABC):
    """Interface defining invoice data access operations."""
    
    @abstractmethod
    def save(self, invoice: Invoice, user_id: int) -> Invoice:
        """Save an invoice to the database."""
    
    @abstractmethod
    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """Retrieve an invoice by its ID."""
    
    @abstractmethod
    def list_overdue(self, as_of: date = None) -> List[Invoice]:
        """List all overdue invoices."""

# Database-Specific Repository
class DjangoInvoiceRepository(InvoiceRepository):
    """Django ORM implementation of the invoice repository."""
    
    def _to_domain(self, db_invoice: DjangoInvoice) -> DomainInvoice:
        """Convert Django model to domain model."""
        return DomainInvoice(
            amount=db_invoice.amount,
            due_date=db_invoice.due_date,
            invoice_number=db_invoice.invoice_number,
            file_path=db_invoice.file_path,
            invoice_id=db_invoice.id
        )

    def save(self, invoice: DomainInvoice, user_id: int) -> DomainInvoice:
        """Save an invoice to the database."""
        db_invoice = self._to_django(invoice, user_id)
        db_invoice.save()
        return self._to_domain(db_invoice)

    def list_overdue(self, as_of: date = None) -> List[DomainInvoice]:
        """List all overdue invoices."""
        check_date = as_of or date.today()
        db_invoices = DjangoInvoice.objects.filter(
            Q(due_date__lt=check_date) & Q(status='pending')
        )
        return [self._to_domain(invoice) for invoice in db_invoices]
```

Let's break down this code:

#### Abstract Base Class (ABC)
`ABC` stands for Abstract Base Class. It's a Python feature that helps define interfaces:
- An interface is like a contract that other classes must follow
- Classes that inherit from ABC must implement all its abstract methods
- You can't create an instance of an ABC directly; it's meant to be inherited
- It ensures that all repository implementations have the same methods

#### Base Repository (Interface)
```python
class InvoiceRepository(ABC):
```
- Defines the base interface that all invoice repositories must implement
- Inherits from ABC to make it an abstract base class
- Acts as a contract for different repository implementations

```python
@abstractmethod
def save(self, invoice: Invoice, user_id: int) -> Invoice:
```
- `@abstractmethod`: Marks this method as required in any implementing class
- `invoice: Invoice`: Takes a domain Invoice object as input
- `user_id: int`: Takes the ID of the user performing the action
- `-> Invoice`: Returns a domain Invoice object after saving

```python
def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
```
- Takes an invoice ID as input
- `Optional[Invoice]`: Returns either an Invoice object or None if not found
- `Optional` is used because the invoice might not exist

```python
def list_overdue(self, as_of: date = None) -> List[Invoice]:
```
- `as_of: date = None`: Optional date parameter, defaults to None
- `-> List[Invoice]`: Returns a list of domain Invoice objects
- Used to find all overdue invoices as of a specific date

#### Django Implementation
```python
class DjangoInvoiceRepository(InvoiceRepository):
```
- Concrete implementation of the InvoiceRepository interface
- Uses Django's ORM to interact with the database

```python
def _to_domain(self, db_invoice: DjangoInvoice) -> DomainInvoice:
```
- Private method (indicated by _) for internal use
- Converts a Django model instance to a domain model
- Maps database fields to domain object properties

```python
def save(self, invoice: DomainInvoice, user_id: int) -> DomainInvoice:
```
1. Takes a domain invoice and user ID
2. Converts domain model to Django model
3. Saves to database
4. Converts back to domain model and returns it

```python
def list_overdue(self, as_of: date = None) -> List[DomainInvoice]:
```
1. `check_date = as_of or date.today()`: Uses provided date or today
2. `Q(due_date__lt=check_date)`: Finds invoices due before check_date
3. `& Q(status='pending')`: Only includes pending invoices
4. Returns list of converted domain models

### How it Works
Here's how data flows through our system when working with invoices:

1. **Creating/Updating an Invoice:**
```
[Domain Invoice] → [Repository._to_django()] → [Django Invoice] → [Database]
   (Business)         (Conversion)            (Persistence)       (Storage)
```

2. **Retrieving an Invoice:**
```
[Database] → [Django Invoice] → [Repository._to_domain()] → [Domain Invoice]
 (Storage)    (Persistence)      (Conversion)              (Business)
```

### Practical Example
```python
# Without Repository Pattern (Direct Database Access):
invoice = Invoice.objects.get(id=123)  # Directly coupled to Django ORM
invoice.amount = 500
invoice.save()

# With Repository Pattern:
invoice = invoice_repository.get(id=123)  # Domain doesn't know about database
invoice.update_amount(500)  # Business logic in domain model
invoice_repository.save(invoice)  # Repository handles persistence
```

### Combined approach and alternatives considered
We considered several alternative approaches:
   
1. **Single Django Model/Active Record Pattern** (Traditional Django approach)
   - Combines data access and business logic in one model
   - Problems:
     * Mixed Concerns: Database details get mixed with business rules
     * Testing Difficulty: Can't test business logic without database
     * Less Flexible: Changing database structure affects business logic
     * Framework Lock-in: Business logic becomes tied to Django
   - While simpler initially, becomes harder to maintain as complexity grows
   - Pros: Simpler, less code initially
   - Cons: Tighter coupling, harder to change, mixed concerns

Here's how it would look if we combined business logic and persistence (the Active Record Pattern):

```python
class Invoice(models.Model):
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    manual_urgency = models.IntegerField(null=True, blank=True)
    
    def calculate_urgency(self) -> int:
        if self.manual_urgency:
            return self.manual_urgency
        days_until_due = (self.due_date - date.today()).days
        if days_until_due < 0:
            return 1  # Overdue
        elif days_until_due < 7:
            return 2  # Critical
        # ... etc
```
   
2. **Direct Database Access**
   - Business logic directly uses database queries
   - Leads to tight coupling between business logic and storage
   - Makes testing and maintenance more difficult
   - Offers no abstraction for different storage strategies
   - Pros: More straightforward, familiar to many developers
   - Cons: Tight coupling, difficult testing, no abstraction layer

Here's how it would look with direct database access:

```python
def calculate_invoice_urgency(invoice_id: int) -> int:
    # Business logic directly coupled with database queries
    invoice = Invoice.objects.get(id=invoice_id)
    
    # Direct database query for related data
    payments = Payment.objects.filter(invoice_id=invoice_id)
    if payments.exists():
        return 0  # Not urgent if any payments exist
    
    # Complex business logic mixed with database operations
    overdue_count = Invoice.objects.filter(
        customer_id=invoice.customer_id,
        due_date__lt=date.today(),
        status='unpaid'
    ).count()
    
    days_until_due = (invoice.due_date - date.today()).days
    
    # Business rules mixed with database concerns
    if days_until_due < 0:
        # Update status directly in database
        invoice.status = 'overdue'
        invoice.save()
        return 1  # Overdue
    elif days_until_due < 7 and overdue_count > 0:
        return 2  # Critical
    else:
        return 3  # Normal
```

3. **Pure Domain Model (Our Chosen Approach)** 
   See [Benefits and Rationale](#benefits-and-rationale) for details on why we chose this approach.

### Technology independence
- Business logic remains independent of storage technology
- Can switch databases without changing domain code (e.g. PostgreSQL to SQL Server)
- Multiple implementations can coexist (e.g., cached, audited versions)

Below are conceptual examples to illustrate how different storage implementations could work while maintaining the same interface. Note that these are not actual implementations but rather pseudocode to demonstrate the concepts:

```python
# Our actual PostgreSQL implementation is shown in the Repository Pattern section above

# CONCEPTUAL EXAMPLES - Not actual implementations

# Example: How a MongoDB implementation might look
class MongoInvoiceRepository(InvoiceRepository):
    """Conceptual example of MongoDB storage."""
    def save(self, invoice: Invoice, user_id: int) -> Invoice:
        # Pseudocode: Convert domain model to MongoDB document
        document = {
            'amount': float(invoice.amount),
            'due_date': invoice.due_date.isoformat(),
            'invoice_number': invoice.invoice_number,
            'uploaded_by': user_id
        }
        # Pseudocode: Store in MongoDB
        result = mongo_collection.insert_one(document)
        return self._to_domain(document)

    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        # Pseudocode: MongoDB query
        document = mongo_collection.find_one({'_id': invoice_id})
        return self._to_domain(document) if document else None

# Example: How feature enhancements might look
class CachedInvoiceRepository(InvoiceRepository):
    """Conceptual example of adding caching."""
    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        # Pseudocode: Check cache first
        if cached := cache.get(f"invoice:{invoice_id}"):
            return cached
        invoice = super().get_by_id(invoice_id)
        if invoice:
            cache.set(f"invoice:{invoice_id}", invoice)
        return invoice

class AuditedInvoiceRepository(InvoiceRepository):
    """Conceptual example of adding audit logging."""
    def save(self, invoice: Invoice, user_id: int) -> Invoice:
        # Pseudocode: Add audit logging
        audit_log.record("Saving invoice", invoice, user_id)
        return super().save(invoice, user_id)
```

These conceptual examples demonstrate how:
- Different storage technologies could be supported
- Additional features could be added through composition
- The interface remains consistent regardless of implementation
- The domain model stays unaware of storage details

Note: The actual implementation would require proper error handling, validation, and additional methods to fully implement the interface.

## Understanding Simplified Unit Testing Setup

Our approach enables streamlined testing through mock repositories - simplified implementations used specifically for testing. This setup provides several key advantages:

1. **Mock Repository Benefits**
   - Control test scenarios easily
   - Test business logic without database dependencies
   - Make tests run faster and more reliably
   - Simulate edge cases and error conditions

2. **Simplified Test Structure**
   - Easier to write and understand tests
   - More focused on business logic
   - Less dependent on infrastructure
   - Clearer test intent

3. **Practical Advantages**
   - No Database Setup Required
     * No need to create test databases
     * No need to run migrations
     * No need to clean up after tests
   
   - Faster Test Execution
     * Tests run in memory
     * No database operations
     * No network calls
   
   - Easier Maintenance
     * Less code to maintain
     * Fewer moving parts
     * Less likely to break due to infrastructure changes

Example of testing with mock repositories:

```python
# Example 1: Testing basic business rules
def test_invoice_urgency_calculation():
    # Setup mock repository - no real database needed
    mock_repo = MockInvoiceRepository()
    
    # Test business logic without database
    invoice = Invoice(due_date=date.today() + timedelta(days=5))
    assert invoice.calculate_urgency() == UrgencyLevel.CRITICAL

# Example 2: Testing error conditions
def test_invoice_not_found():
    # Mock repository can simulate database errors
    mock_repo = MockInvoiceRepository()
    mock_repo.simulate_error('not_found')  # Pseudocode
    
    result = mock_repo.get_by_id(123)
    assert result is None

# Example 3: Testing complex business scenarios
def test_overdue_invoice_processing():
    # Mock repository with predefined test data
    mock_repo = MockInvoiceRepository([
        Invoice(due_date=date.today() - timedelta(days=10)),
        Invoice(due_date=date.today() + timedelta(days=10))
    ])
    
    # Business logic only sees domain models
    overdue = mock_repo.list_overdue()
    assert len(overdue) == 1
    assert overdue[0].is_overdue()

# Example 4: Testing with different repository behaviors
def test_invoice_saving_with_audit():
    # Compose repositories to test feature interactions
    mock_repo = MockInvoiceRepository()
    audited_repo = AuditedInvoiceRepository(mock_repo)
    
    invoice = Invoice(amount=100)
    audited_repo.save(invoice, user_id=1)
    
    # Can verify both save and audit occurred
    assert mock_repo.was_saved(invoice)
    assert mock_repo.was_audited(invoice)
```

These examples show how mock repositories help us:
1. Test business rules in isolation
2. Simulate error conditions easily
3. Set up complex test scenarios
4. Test feature combinations
All without needing a real database or complex setup.

## Related decisions
- [Urgency field type](./urgency_field_type.md)
