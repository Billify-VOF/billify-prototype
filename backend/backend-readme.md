# Billify Backend

Django-based backend for the Billify application, designed with a clean separation of concerns across various layers for better scalability and maintainability.

## Prerequisites

Ensure you have the following installed:
- Python 3.11 or higher
- PostgreSQL 15.x or higher
- Tesseract OCR

For installation instructions, refer to the main README.md.

## Quick Start

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install --upgrade pip
   # For development (includes testing and debugging tools)
   pip install -r config/requirements/development.txt
   # For production (only required packages)
   pip install -r config/requirements/base.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Required settings in `.env`:
   ```bash
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=postgres://billify:your_password@localhost:5432/billify
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   ```

4. Set up the database:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
backend/
├── api/                      # API endpoints and routing
│   ├── serializers/         # Data serialization
│   ├── urls.py             # API URL routing
│   └── views/              # API view implementations
├── apps/                    # Django applications
│   ├── README.md           # Apps documentation
│   ├── accounts/           # User management
│   │   ├── admin.py       # Django admin configuration
│   │   ├── apps.py        # App configuration
│   │   ├── models.py      # Database models
│   │   ├── tests/         # App-specific tests
│   │   └── views.py       # View logic
│   ├── cashflow/          # Cash flow management
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tests/
│   │   └── views.py
│   └── invoices/          # Invoice processing
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── tests/
│       └── views.py
├── config/                 # Project configuration
│   ├── README.md          # Configuration documentation
│   ├── settings/          # Environment-specific settings
│   │   ├── base.py       # Base settings
│   │   ├── development.py # Development overrides
│   │   └── production.py # Production overrides
│   └── requirements/      # Dependencies
│       ├── base.txt      # Core dependencies
│       ├── development.txt # Development tools
│       └── production.txt # Production requirements
├── domain/                # Business logic
│   ├── models/           # Domain models
│   │   ├── invoice.py
│   │   └── user.py
│   ├── services/         # Business services
│   │   ├── invoice_service.py
│   │   └── cashflow_service.py
│   ├── repositories/interfaces/
│   │   ├── invoice_repository.py
│   │   └── cashflow_repository.py
│   └── exceptions.py     # Domain exceptions
├── infrastructure/       # Technical infrastructure
│   ├── django/          # Django-specific implementations
│   │   ├── models/      # ORM models
│   │   └── repositories/ # Data access
│   ├── migrations/      # Database migrations
│   └── storage/        # File storage implementations
├── integrations/       # External services
│   ├── providers/     # Service providers
│   ├── transformers/  # Data transformers
│   │   └── pdf/      # PDF processing
│   └── sync/         # Synchronization tasks
├── media/            # Uploaded files storage
├── tests/            # Test suite
│   ├── integration/  # Integration tests
│   └── e2e/         # End-to-end tests
├── .env.example     # Environment variables template
├── .gitkeep         # Git directory marker
├── manage.py        # Django CLI
├── pyproject.toml   # Python project metadata
├── pylintrc.ini     # Pylint configuration
├── setup.cfg        # Project configuration
└── setup.py        # Package setup
```

## Architecture Overview

The backend follows a layered architecture with clear separation of concerns:

### 1. API Layer (`apps/api/`)
- REST endpoints
- Request/response handling
- Authentication & permissions
- Data validation

### 2. Domain Layer (`domain/`)
- Core of the application, encapsulating business rules and logic.
- Framework-agnostic and independent of storage or API concerns.
- Key components:
   - Models: Pure Python representations of business entities.
   - Services: Business logic for financial calculations and validations.
   - Exceptions: Domain-specific error handling.
- Domain models
- Domain services  

### 3. Infrastructure Layer (`infrastructure/`)
- Django-specific implementations
- ORM models
- Data access

### 4. Integration Layer (`integrations/`)
- External service integration
- Data transformation
- File processing
- Synchronization tasks

### Code Style
- Follow PEP 8
- Use type hints
- Document functions and classes
- Keep functions focused and small

## Domain Organization

Each domain represents a core business area and is structured as follows:

```
domain/
├── models/                   # Domain models (not tied to Django ORM)
├── services/                 # Business logic
├── repositories/             # Abstract data access interfaces
└── exceptions.py             # Domain-specific exceptions
```

### Why Use a Domain-Driven Design?

- **Separation of Concerns**: Each domain encapsulates its logic, keeping unrelated concerns isolated.
- **Reusable Logic**: Domain services can be reused across multiple parts of the application.
- **Testability**: Framework-independent code is easier to test and maintain.
- **Scalability**: Clean boundaries between domains make it easier to scale features independently.

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

---

## Development

- **Run Tests**:
   ```bash
   pytest
   ```

- **Code Formatting**:
   ```bash
   black .
   ```

- **Linting**:
   ```bash
   flake8
   ```

---

## Environment-Specific Settings

- Base settings are defined in `billify/settings/base.py`.
- Environment overrides are in:
  - `billify/settings/development.py` (for local development)
  - `billify/settings/production.py` (for production).

To specify the environment, set the `DJANGO_SETTINGS_MODULE` environment variable:
```bash
export DJANGO_SETTINGS_MODULE=billify.settings.development
```

---

## Dependencies

- Base dependencies: `requirements/base.txt`
- Development-specific tools: `requirements/development.txt`
- Production dependencies: `requirements/production.txt`

---

## Testing

### Directory Structure

```
backend/
├── tests/                      # Main test directory
│   ├── conftest.py            # Pytest configuration and fixtures
│   ├── integration/           # Integration tests
│   │   ├── test_invoice_flow.py
│   │   └── test_api.py
│   └── e2e/                   # End-to-end tests
│       └── test_invoice_processing.py
└── apps/                      # App-specific unit tests
    ├── accounts/tests/
    ├── invoices/tests/
    └── cashflow/tests/
```

### Test Categories

1. **Unit Tests** (`apps/*/tests/`)
   - Component isolation
   - Fast execution
   - No external dependencies

2. **Integration Tests** (`tests/integration/`)
   - Component interaction
   - Database operations
   - API endpoints

3. **End-to-End Tests** (`tests/e2e/`)
   - Complete workflows
   - External services
   - User scenarios

### Running Tests

```bash
# Run all tests
pytest

# Run specific categories
pytest tests/integration/
pytest tests/e2e/
pytest apps/

# Run with coverage
pytest --cov=backend
```

### Best Practices
1. Follow AAA pattern (Arrange, Act, Assert)
2. Use meaningful test names
3. One assertion per test when possible
4. Mock external services
5. Use fixtures for setup
6. Keep tests focused and isolated

## Environment Configuration

The project uses different settings for different environments:

- `base.py`: Common settings
- `development.py`: Local development
- `production.py`: Production environment

To specify the environment:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.development
```

## API Documentation

Access the API documentation at:
- Swagger UI: http://localhost:8000/api/docs/
- Admin Interface: http://localhost:8000/admin/

## Troubleshooting

1. **Database Issues**
   - Verify PostgreSQL is running
   - Check credentials in `.env`
   - Ensure migrations are applied

2. **Environment Issues**
   - Verify virtual environment is active
   - Check `DJANGO_SETTINGS_MODULE`
   - Validate environment variables

3. **PDF Processing**
   - Verify Tesseract installation
   - Check PATH configuration
   - Validate file permissions

### Git Workflow
1. Create feature branches from `main`
2. Write descriptive commit messages
3. Get code review before merging
4. Keep PRs focused and small