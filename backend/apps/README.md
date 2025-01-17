# apps/README.md

# Django Applications

This directory contains Django application configurations. These apps handle framework-specific setup but should not contain business logic.

## Structure

- `accounts/` - User management
  - `admin.py` - Django admin interface configuration
  - `apps.py` - Django app configuration
  - `models.py` - Database models
  - `views.py` - View logic
  - `tests/` - App-specific unit tests
    - `test_models.py`
    - `test_views.py`

- `cashflow/` - Cash flow management
  - Similar structure to accounts

- `invoices/` - Invoice processing
  - Similar structure to accounts

## Guidelines

- Keep apps focused on Django configuration
- Avoid putting business logic here
- Use for framework-specific features (admin, signals)
- Keep tests focused on Django-specific functionality