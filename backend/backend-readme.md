
# Billify Backend

Django-based backend for the Billify application, designed with a clean separation of concerns across various layers for better scalability and maintainability.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements/base.txt  # Use the appropriate environment file (e.g., development.txt)
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

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
backend/
├── billify/                  # Django project directory
│   ├── __init__.py
│   ├── settings/             # Environment-specific settings
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py               # URL configurations
│   └── wsgi.py               # WSGI configuration
├── apps/                     # Django applications
│   ├── accounts/             # User management
│   ├── invoices/             # Invoice handling
│   │   ├── repositories/     # Abstract data access layer
│   │   └── views.py          # API endpoints
│   ├── cashflow/             # Cash flow calculations
│   ├── api/                  # API layer for REST endpoints
│   │   ├── urls.py
│   │   └── views/
│   │       ├── core.py
│   │       └── integration.py
│   ├── domain/               # Domain-specific business logic
│   │   ├── models/           # Business models
│   │   ├── services/         # Domain services
│   │   └── exceptions.py     # Domain-specific exceptions
│   └── integrations/         # External system interactions and transformations
│       ├── providers/        # External provider handlers
│       ├── transformers/     # Data transformation utilities
│       ├── sync/             # Synchronization tasks
│       └── object_storage.py # Object storage management
├── core/                     # Shared utilities and services
│   ├── models.py
│   ├── services.py
│   └── utils.py
├── requirements/             # Dependencies
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── tests/                    # Test cases
└── manage.py                 # Django management script
```

## Layered Architecture

The Billify backend is designed with a clear separation of concerns into multiple layers:

### 1. **Presentation Layer**
   - Located in the frontend repository (React application).
   - Interacts with the backend through REST API endpoints defined in the `api/` app.

### 2. **Application Layer**
   - Handles HTTP requests, authentication, and routing.
   - Defines API endpoints and coordinates interactions between layers.
   - Key components:
     - API views (`apps/api/views`)
     - Serializers for data validation
     - URL routing

### 3. **Integration Layer**
   - Manages external system interactions (e.g., OCR, data synchronization).
   - Transforms external data formats into standardized formats used internally.
   - Key components:
     - `apps/integrations/` for provider-specific logic, transformers, and synchronization.

### 4. **Domain Layer**
   - Core of the application, encapsulating business rules and logic.
   - Framework-agnostic and independent of storage or API concerns.
   - Key components:
     - Models: Pure Python representations of business entities.
     - Services: Business logic for financial calculations and validations.
     - Exceptions: Domain-specific error handling.

### 5. **Data Layer**
   - Handles data persistence and retrieval using Django ORM.
   - Abstracted through repository patterns in `apps/invoices/repositories/`.

---

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

This README reflects the updated structure and provides a comprehensive guide to the refactored backend. Let me know if you'd like to expand on any section!
