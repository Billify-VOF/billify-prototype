# API Layer

The API layer handles HTTP-related concerns and serves as the interface between our frontend and backend services.

## Structure

- `views/` - HTTP request handlers organized by domain
  - `invoice.py` - Invoice management and processing endpoints
  - `accounts.py` - User account management endpoints (planned)
  - `cash_flow.py` - Cash flow related endpoints (planned)

- `serializers.py` - Data transformation for API requests/responses
- `urls.py` - API routing configuration

## API Documentation

- API Root: `http://localhost:8000/` (provides overview and health check)

## Available Endpoints

- `/api/invoices/` - Invoice management
  - `POST`: Upload and process new invoices
  - `GET`: List and filter processed invoices

Future endpoints (planned):
- `/api/cash-flow/` - Cash flow analytics
- `/api/accounts/` - User account management

## Guidelines

- Keep views thin - delegate business logic to domain services
- Focus on HTTP concerns (request parsing, response formatting)
- Handle authentication and authorization
- Use serializers for data validation and transformation
- Maintain consistent error responses across endpoints
- Document API endpoints using docstrings and OpenAPI decorators

## Authentication

Currently using:
- Session Authentication
- Basic Authentication

Authentication is optional during development (AllowAny permission class).

## Error Handling

Maintain consistent error responses:
```json
{
    "error": "string",
    "detail": "string",
    "code": "string"
}
```

## CORS Configuration

CORS is enabled for development with:
- Default origin: `http://localhost:3000`
- Allowed methods: GET, POST, PUT, PATCH, DELETE, OPTIONS