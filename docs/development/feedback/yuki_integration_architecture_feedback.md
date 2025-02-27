# Yuki Integration Architecture Feedback

## Overview

This document provides feedback on the proposed Yuki Integration MVP implementation, evaluating its alignment with Billify's current architecture, domain models, and Domain-Driven Design (DDD) principles.

## Key Misalignments with Current Architecture

### 1. Django Model vs. Domain Model Approach
The documentation proposes a direct Django model implementation:
```python
class Invoice(models.Model):
    # Django model fields...
```

This **conflicts with the project's DDD approach**, which separates:
- Domain models (in `backend/domain/models/`) that contain business logic
- Django models (in `infrastructure/django/models/`) that handle persistence
- Repository interfaces as abstractions between them

### 2. Missing Domain Layer

The proposed implementation bypasses the domain layer entirely by:
- Defining business rules directly in Django models
- Missing value objects (like `InvoiceStatus` from existing code)
- Not separating business concerns from persistence concerns

### 3. Repository Pattern Omission

The documentation doesn't mention:
- Repository interfaces that define data access contracts
- Concrete implementations that bridge domain and persistence
- Converting between domain and infrastructure models

### 4. Direct Database Manipulation

The documentation suggests directly manipulating the database:
```python
def sync_invoices():
    fetch_invoices()  # Direct database operations
```

This contradicts our current approach where:
- Business operations go through domain services
- Data persistence happens through repositories
- Domain models maintain business invariants

## Recommendations for Alignment

### 1. Create a Dedicated Domain Entity
```python
# domain/models/yuki_invoice.py
class YukiInvoice:
    def __init__(
        self,
        *,
        invoice_number: str,
        type: str,  # 'purchase' or 'sales'
        issue_date: date,
        due_date: date,
        total_amount: Decimal,
        payment_status: InvoiceStatus,
        yuki_invoice_id: str,
        invoice_id: Optional[int] = None
    ):
        # Initialize fields
        # Add validation
```

### 2. Define Repository Interface
```python
# domain/repositories/interfaces/yuki_invoice_repository.py
class YukiInvoiceRepository(ABC):
    @abstractmethod
    def save(self, invoice: YukiInvoice, user_id: int) -> YukiInvoice:
        """Save a Yuki invoice to the database"""
        
    @abstractmethod
    def get_by_yuki_id(self, yuki_id: str) -> Optional[YukiInvoice]:
        """Get invoice by Yuki ID"""
    
    # Other methods...
```

### 3. Create Integration Service
```python
# domain/services/yuki_integration_service.py
class YukiIntegrationService:
    def __init__(self, invoice_repository: YukiInvoiceRepository):
        self.repository = invoice_repository
        
    def process_yuki_invoice(self, yuki_data: dict) -> YukiInvoice:
        """Convert Yuki API data to domain model and save"""
        # Business logic to process invoice data
        # Return domain model
```

### 4. Infrastructure Implementation
```python
# infrastructure/django/models/yuki_invoice.py
class YukiInvoice(models.Model):
    # Django model fields from the PDF
    
# infrastructure/django/repositories/yuki_invoice_repository.py
class DjangoYukiInvoiceRepository(YukiInvoiceRepository):
    # Implementation of repository interface
    
# infrastructure/integrations/yuki_client.py
class YukiClient:
    # API communication logic
```

### 5. Celery Task Refactor
```python
@shared_task
def sync_invoices():
    # Get dependencies through DI
    yuki_client = get_yuki_client()
    yuki_repository = get_yuki_repository()
    integration_service = YukiIntegrationService(yuki_repository)
    
    # Use domain services instead of direct DB operations
    yuki_data = yuki_client.fetch_invoices()
    for invoice_data in yuki_data:
        integration_service.process_yuki_invoice(invoice_data)
```

## Design Considerations

### Integration with Existing Invoice Model
Consider how Yuki invoices relate to the existing `Invoice` domain model:
- Are they completely separate concepts?
- Should you extend the existing invoice model?
- How will you handle mapping between Yuki invoices and your domain invoices?

### Value Objects
For proper DDD implementation:
- Create specific value objects for Yuki-specific concepts
- Reuse existing ones like `InvoiceStatus` where appropriate
- Consider creating a `YukiInvoiceType` enum for 'purchase' and 'sales'

### Business Rules
Define clear business rules in the domain layer:
- What validation rules apply to Yuki invoices?
- Do urgency calculations apply to Yuki invoices?
- What business operations are allowed on Yuki invoices?

## Conclusion

The current proposal needs significant restructuring to align with Billify's Domain-Driven Design architecture. Implementing the recommendations above will ensure the Yuki integration maintains the separation of concerns, clean architecture, and business-focus that characterizes the rest of the system. 