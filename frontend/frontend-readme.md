# Billify Frontend

Next.js-based frontend for the Billify application, built with TypeScript and Tailwind CSS.

## Prerequisites

Ensure you have the following installed:

- Node.js 18.x or higher
- npm 9.x or higher

For installation instructions, refer to the main README.md.

## Quick Start

1. Install dependencies:

   ```bash
   npm install
   ```

2. Set up environment variables:

   ```bash
   cp .env.example .env.local
   ```

   Required settings in `.env.local`:

   ```bash
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Project Structure

```
frontend/
├── app/                    # Next.js 13 app directory
│   ├── dashboard/         # Dashboard page
│   ├── api/              # API routes
│   ├── lib/              # App-specific utilities
│   ├── globals.css      # Global styles
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Root page
├── components/           # React components
│   ├── ui/             # UI components
│   ├── InvoiceUploadResult.tsx
│   └── PDFViewerWrapper.tsx
├── lib/                 # Shared utilities
│   └── utils.ts        # Utility functions
├── styles/             # Additional styles
├── public/             # Static assets
└── node_modules/       # Dependencies
```

## Development Guidelines

### Code Standards

- Use TypeScript for type safety
- Follow ESLint and Prettier configurations
- Use Tailwind CSS for styling
- Follow React best practices and hooks

### Component Organization

- Keep components focused and reusable
- Use proper TypeScript types
- Document props and functionality
- Follow atomic design principles

### State Management

- Use React Context for global state
- Keep component state local when possible
- Use React Query for API state
- Implement proper error handling

## Testing

### Directory Structure

```
frontend/
├── __tests__/                 # Jest tests directory
│   ├── components/            # Component tests
│   │   ├── InvoiceList.test.tsx
│   │   └── UploadDialog.test.tsx
│   ├── pages/                 # Page tests
│   │   └── dashboard.test.tsx
│   └── utils/                 # Utility function tests
│       └── formatters.test.ts
└── cypress/                   # E2E tests
    ├── e2e/                   # Test specs
    │   ├── invoice-upload.cy.ts
    │   └── dashboard.cy.ts
    └── fixtures/              # Test data
        └── sample-invoice.pdf
```

### Test Categories

1. **Unit Tests** (`__tests__/`)

   - Component testing with Jest and React Testing Library
   - Utility function testing
   - State management testing

2. **End-to-End Tests** (`cypress/`)
   - Full user flow testing
   - Cross-browser testing
   - Integration with backend API

### Running Tests

```bash
# Run unit tests
npm test

# Run unit tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch

# Run Cypress tests
npm run cypress:open  # Interactive mode
npm run cypress:run  # Headless mode
```

### Best Practices

1. Test user interactions, not implementation
2. Use data-testid for test selectors
3. Mock API calls and external services
4. Write accessible tests
5. Test error states and loading states
6. Keep tests focused and isolated

## Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run format       # Run Prettier

# Testing
npm test            # Run Jest tests
npm run cypress     # Run Cypress tests
```

## Environment Configuration

The frontend uses the following environment variables:

```bash
# Required
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000  # Backend API URL

# Optional
NEXT_PUBLIC_DEBUG=true                        # Enable debug mode
```

## Troubleshooting

1. **Build Issues**

   - Clear `.next` directory
   - Delete `node_modules` and reinstall
   - Verify Node.js version

2. **API Connection**

   - Check backend URL in `.env.local`
   - Verify backend is running
   - Check CORS settings

3. **Test Issues**
   - Clear Jest cache: `npm test -- --clearCache`
   - Update test snapshots: `npm test -- -u`
   - Check Cypress configuration
