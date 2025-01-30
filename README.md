# Billify

⚠️ **PROPRIETARY SOFTWARE NOTICE**: This is proprietary software owned by Billify. All rights reserved.
Unauthorized copying, modification, distribution, or use is strictly prohibited.

## Overview

Billify is a proprietary cash flow management and invoice tracking system designed 
for small to medium-sized enterprises.

## Our philosophy: Move fast and break things

At Billify, we embrace the "move fast and break things" philosophy, which emphasizes rapid innovation and iterative development. This approach means:

- **Speed over perfection**: We prioritize quick iterations and learning from real-world feedback over perfect but delayed solutions.
- **Continuous innovation**: We're not afraid to try new approaches and pivot quickly when needed.
- **Fail fast, learn faster**: We view failures as valuable learning opportunities that help us build better solutions.
- **User-driven development**: We rapidly respond to user feedback, even if it means breaking existing patterns.
- **Trial and error development**: We build through experimentation and learning from attempts, rather than trying to design everything perfectly upfront—using any available resources (documentation, StackOverflow, AI) to generate working solutions and iterating until we get it right.

This philosophy extends to our coding practices:

- **Ship working code first**: We believe in getting functional code out quickly, then improving it later.
- **Features over perfection**: Perfect code shouldn't block shipping new features.
- **Embrace technical debt**: Technical debt is acceptable when intentional and tracked—we can refactor later.
- **Quick iterations**: We prioritize getting solutions to users fast, even if the implementation isn't ideal.
- **Dead code management**: We remove dead code when we notice it, but don't actively hunt for it.
- **Validate through usage**: This approach helps us validate ideas quickly and ensure we're building features that matter to users rather than spending time perfecting code that might not meet real-world needs.

## Documentation

For more detailed setup and development instructions, refer to:
- Backend documentation: `backend/backend-readme.md`
- Frontend documentation: `frontend/frontend-readme.md`
- Architecture overview: `docs/architecture/overview.md`

## Prerequisites

Before setting up the project, ensure you have the following installed:

### System requirements
These are the system-level packages that must be installed before the Python packages can work:

- Python 3.11 or higher (required for backend)
- Node.js 18.x or higher (required for frontend)
- PostgreSQL 15.x or higher (required for database)
- Tesseract OCR (required for PDF text extraction)

### System package installation

#### Windows:
1. Install Python:
   - Download Python 3.11 or higher from the [official website](https://www.python.org/downloads/windows/)
   - Run the installer
   - **Important**: Check "Add Python to PATH" during installation
   - Verify installation:
     ```cmd
     python --version
     pip --version
     ```

2. Install Node.js:
   - Download Node.js 18.x LTS from the [official website](https://nodejs.org/)
   - Run the installer (it will automatically add Node.js to PATH)
   - Verify installation:
     ```cmd
     node --version
     npm --version
     ```

3. Install PostgreSQL:
   - Download the PostgreSQL installer for Windows from the [official website](https://www.postgresql.org/download/windows/)
   - Run the installer and follow the setup wizard
   - Remember the password you set for the postgres user
   - Add PostgreSQL to your system PATH if the installer didn't do it automatically
   
4. Install Tesseract OCR:
   - Download the Tesseract installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Run the installer and follow the setup wizard
   - Add Tesseract to your system PATH:
     1. Open System Properties > Advanced > Environment Variables
     2. Under System Variables, find and select "Path"
     3. Click "Edit" and add the Tesseract installation directory (typically `C:\Program Files\Tesseract-OCR`)
     4. Click "OK" to save

5. Verify all installations:
   ```cmd
   :: Check Python
   python --version
   pip --version
   
   :: Check Node.js
   node --version
   npm --version
   
   :: Check PostgreSQL
   psql --version
   
   :: Check Tesseract
   tesseract --version
   ```

#### macOS (using Homebrew):
```bash
# Install Python 3.11
brew install python@3.11
# After installation, Homebrew will show instructions on how to add Python to your PATH
# Usually by adding something like this to your ~/.zshrc or ~/.bash_profile:
# export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"

# Install Node.js 18
brew install node@18
# Follow Homebrew's instructions to add Node.js to your PATH if needed

# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Tesseract
brew install tesseract

# Verify installations
python3.11 --version  # Make sure it shows 3.11.x
pip3 --version
node --version       # Make sure it shows v18.x
npm --version
psql --version
tesseract --version
```

Note: After installing Python and Node.js, you might need to restart your terminal for the PATH changes to take effect.

#### Ubuntu/Debian:
```bash
# Install Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PostgreSQL
sudo apt-get install postgresql-15

# Install Tesseract
sudo apt-get install tesseract-ocr

# Verify installations
python3.11 --version
pip3 --version
node --version
npm --version
psql --version
tesseract --version
```

### Python dependencies
The project's Python dependencies are managed through requirements files:
- `backend/config/requirements/base.txt`: Core dependencies required to run the application
- `backend/config/requirements/development.txt`: Additional tools for development (testing, debugging, etc.)

These will be installed during the backend setup process.

## Project setup

### Database setup

The project uses PostgreSQL to store invoice data, including:
- Invoice metadata (number, amount, due date)
- File paths to uploaded PDFs
- Processing status and timestamps

Current database state:
1. The database schema is defined but needs to be set up
2. Migrations exist and need to be applied
3. No data has been stored yet

To set up the database:

1. Create a database and user:
   ```bash
   # Connect to PostgreSQL
   sudo -u postgres psql

   # Create database and user (in psql)
   CREATE DATABASE billify;
   CREATE USER billify WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE billify TO billify;
   \q
   ```

2. Configure database connection:
   - Create a `.env` file in the `backend` directory
   - Add database configuration:
     ```
     DATABASE_URL=postgres://billify:your_password@localhost:5432/billify
     ```

3. Apply migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```

### Environment configuration

1. Backend (`.env`):
   ```bash
   # Required settings
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=postgres://billify:your_password@localhost:5432/billify
   
   # Optional settings
   ALLOWED_HOSTS=localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   ```

2. Frontend (`.env.local`):
   ```bash
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

## Backend setup

1. Create and activate a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   # For development (includes testing and debugging tools):
   pip install -r config/requirements/development.txt
   # For production (only required packages):
   pip install -r config/requirements/base.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your local configuration (database credentials, etc.)

4. Set up the database:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Frontend setup

1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env.local
   ```
   Edit `.env.local` with your local configuration

3. Start the development server:
   ```bash
   npm run dev
   ```

## Development guidelines

### Code standards
- Follow PEP 8 for Python code
- Use ESLint and Prettier for TypeScript
- Write meaningful commit messages following conventional commits
- Add type hints in Python and use TypeScript for frontend

### Git workflow
1. Create feature branches from `main`:
   ```bash
   git checkout main
   git checkout -b feature/your-feature-name
   ```
2. Keep commits atomic and well-described
3. Push to origin and create a PR against `main`
4. Ensure CI passes and get code review (set up CI - still to do)
5. Squash and merge when approved

### Testing
- Write unit tests for new features
- Update existing tests when modifying features
- Run the full test suite before committing:
  ```bash
  # Backend
  pytest
  
  # Frontend
  npm run test
  ```

The test suite is organized as follows:
```
backend/
├── apps/                    # Django applications
│   ├── accounts/tests/     # Unit tests for accounts app
│   ├── invoices/tests/     # Unit tests for invoices app
│   └── cashflow/tests/     # Unit tests for cashflow app
└── tests/                  # Integration & E2E tests
    ├── integration/        # Integration tests
    └── e2e/               # End-to-end tests

frontend/
├── __tests__/             # Jest unit tests
│   ├── components/        # Component tests
│   ├── pages/            # Page tests
│   └── utils/            # Utility tests
└── cypress/              # E2E tests
    ├── e2e/             # Test specs
    └── fixtures/        # Test data
```

For detailed information about test organization, writing tests, and best practices:
- Backend tests: See `backend/backend-readme.md#testing`
- Frontend tests: See `frontend/frontend-readme.md#testing`

## Troubleshooting

### Common issues

1. **Database connection errors**:
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database and user exist

2. **Node.js/npm issues**:
   - Clear npm cache: `npm cache clean --force`
   - Delete `node_modules` and reinstall

3. **Python/pip issues**:
   - Verify virtual environment is activated
   - Update pip: `python -m pip install --upgrade pip`

4. **PDF processing issues**:
   - Verify Tesseract is in PATH
   - Check Tesseract installation

## Accessing the application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API documentation: http://localhost:8000/api/docs/
- Admin interface: http://localhost:8000/admin/

For more detailed information, refer to the project wiki.