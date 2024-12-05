# API Layer

The API layer handles HTTP-related concerns and serves as the interface between our frontend and backend services.

## Structure

- `views/` - HTTP request handlers organized by domain
  - `accounts.py` - User account management endpoints
  - `cash_flow.py` - Cash flow related endpoints
  - `invoice.py` - Invoice management endpoints
  - `core.py` - Shared functionality endpoints

- `serializers.py` - Data transformation for API requests/responses
- `urls.py` - API routing configuration

## Guidelines

- Keep views thin - delegate business logic to domain services
- Focus on HTTP concerns (request parsing, response formatting)
- Handle authentication and authorization
- Use serializers for data validation and transformation
- Maintain consistent error responses across endpoints
- Document API endpoints clearly