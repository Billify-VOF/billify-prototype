# Billify Backend

Django-based backend for the Billify application.

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your specific settings
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## Project Structure

```
backend/
├── billify/              # Django project directory
│   ├── __init__.py
│   ├── settings.py       # Project settings
│   ├── urls.py          # URL configurations
│   └── wsgi.py          # WSGI configuration
├── apps/                 # Django applications
│   ├── accounts/        # User management
│   ├── invoices/        # Invoice handling
│   └── cashflow/        # Cash flow calculations
├── tests/               # Test cases
├── requirements.txt     # Project dependencies
└── manage.py           # Django management script
```

## Domain Organization

The Billify backend is organized by business domains rather than technical functions or UI features. Each domain is a self-contained module handling all aspects of a specific business capability:

- `accounts`: User authentication, profiles, and company information 
- `invoices`: Complete invoice lifecycle management and document processing
- `cashflow`: Financial calculations, projections, and cash flow analytics

### Why Domains Instead of Features?

Consider a dashboard that shows cash flow summaries, recent invoices, and account balances. Rather than creating a "dashboard" app that either contains business logic or becomes a thin wrapper around other apps, we keep all related functionality within its respective domain. For example, cash flow calculations live in the cashflow domain regardless of where they're displayed in the UI.

This organization provides:
- Clear responsibility boundaries
- Reusable business logic
- Easier testing and maintenance
- Independent scalability of domains

When adding new features, focus on their business purpose rather than their UI presentation. The same business logic can serve multiple UI components while maintaining clean domain separation.

Each domain follows this structure:

```
domain/
├── models.py    # Data structures
├── services.py  # Business logic
├── views.py     # API endpoints
└── tests.py     # Domain tests
```

## Development

- Run tests: `pytest`
- Check code style: `black .`
- Check linting: `flake8`
