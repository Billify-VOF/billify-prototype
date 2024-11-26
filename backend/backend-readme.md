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

## Development

- Run tests: `pytest`
- Check code style: `black .`
- Check linting: `flake8`
