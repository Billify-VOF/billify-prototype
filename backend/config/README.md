# config/README.md

# Configuration

Project-wide configuration and environment settings.

## Structure

### Settings
Django configuration for different environments:
- `base.py` - Common settings
- `development.py` - Development environment
- `production.py` - Production environment

### Requirements
Python package dependencies:
- `base.txt` - Core dependencies
- `development.txt` - Development tools
- `production.txt` - Production requirements

## Guidelines

- Keep sensitive information in environment variables
- Use appropriate settings for each environment
- Document configuration changes
- Maintain clear dependency organization