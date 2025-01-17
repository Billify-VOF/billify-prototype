# config/README.md

# Configuration

Project-wide configuration and environment settings.

## Structure

### Settings
Django configuration for different environments:
- `base.py` - Common settings including:
  - Database configuration
  - REST Framework settings
  - CORS configuration
  - API documentation (drf-spectacular)
  - Storage settings
  - Authentication
- `development.py` - Development environment settings
- `production.py` - Production environment settings

### Requirements
Python package dependencies:
- `base.txt` - Core dependencies including:
  - Django and DRF
  - Database (PostgreSQL)
  - PDF Processing (Tesseract)
  - Task Queue (Celery)
  - Storage (AWS/S3)
- `development.txt` - Development tools for:
  - Testing
  - Debugging
  - Code quality
  - Documentation
- `production.txt` - Production-specific requirements

## Environment Variables

Required variables:
```bash
# Core
SECRET_KEY=your-secret-key
DEBUG=True/False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Storage (Production only)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_ENDPOINT_URL=your-endpoint
```

## Guidelines

- Keep sensitive information in environment variables
- Use appropriate settings for each environment
- Document configuration changes
- Maintain clear dependency organization
- Use environment-specific settings files for overrides
- Follow the principle of least privilege for security settings

## Usage

To specify the environment:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.development  # For development
export DJANGO_SETTINGS_MODULE=config.settings.production   # For production
```

## Security Considerations

- Never commit sensitive data or credentials
- Use strong SECRET_KEY in production
- Configure ALLOWED_HOSTS appropriately
- Set up proper CORS restrictions
- Enable appropriate security middleware
- Configure secure cookie settings in production