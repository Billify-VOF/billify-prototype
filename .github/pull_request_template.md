# Pull Request Template

## Important Note on Migrations
⚠️ **DO NOT include migration files when creating a PR to the main branch**

To prevent conflicts on the production server:
- Do not include migration files when submitting your PR
- Migration files should only be added directly to the main branch
- Migration files should NOT be added to .gitignore

## Description
<!-- Provide a brief, clear description of what this PR accomplishes -->

## Change Narrative
<!-- This section is REQUIRED. Tell the story of your changes in detail to make reviewing easier -->
<!-- Include the following details: -->
<!-- 1. The problem you're solving and why -->
<!-- 2. Your overall approach and architectural decisions -->
<!-- 3. How the code works step-by-step (the "story" of execution) -->
<!-- 4. Alternatives you considered and why they were rejected -->
<!-- 5. Any technical debt or follow-up work created -->
<!-- 6. Document ALL decisions made during development (architecture, code, operations, library choices, trade-offs) in an ADR in the docs/ folder -->

## Changes Made
<!-- List the specific changes made (bullet points work well) -->
- 
- 
- 

## Related Issues
<!-- Link to any related issues this PR addresses -->
Closes #

## Type of Change
<!-- Mark with an 'x' all that apply -->
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)

## Code Quality
### Type Checking
<!-- Indicate if your code includes type checking -->
- [ ] TypeScript (frontend): Properly typed with interfaces/types for all components, functions, and variables
- [ ] Python (backend): Includes type hints for function parameters and return values
- [ ] No type hints/checks included (please explain why): 

### Documentation
<!-- Verify your code is properly documented -->
- [ ] All functions/methods have descriptive docstrings
- [ ] Every module, function, method, and class has a docstring that clearly explains its purpose and usage
- [ ] Docstrings follow the project's standard format
- [ ] Module-level documentation explains the purpose and usage of the component

## Domain-Driven Design (Backend)
<!-- For backend changes, verify alignment with DDD principles -->
### Architecture Compliance
- [ ] Clear separation between domain, application, and infrastructure layers
- [ ] Domain layer contains only business logic with no external dependencies
- [ ] Application services orchestrate use cases without containing business rules
- [ ] Infrastructure layer handles all technical and external concerns with no business logic

### Domain Layer
- [ ] Business concepts are properly modeled as entities, value objects, or aggregates
- [ ] Entities have identity and lifecycle
- [ ] Value objects are immutable and represent concepts with no identity
- [ ] Aggregates enforce consistency boundaries and invariants
- [ ] Domain events used for cross-aggregate communication
- [ ] Rich domain models with behavior, not anemic data containers

### Application Layer
- [ ] Orchestrates domain objects to implement use cases without containing domain rules
- [ ] Provides a stable API for user interfaces and external systems
- [ ] Manages transactions and coordinates work across multiple domain objects
- [ ] Handles authorization and permission checks
- [ ] Translates between domain objects and application DTOs when needed
- [ ] Contains application services that are thin and focused on specific use cases
- [ ] Application-specific exceptions are properly handled and translated
- [ ] Uses dependency injection to access infrastructure services

### Infrastructure Layer
- [ ] Infrastructure layer properly separates technical concerns from domain logic
- [ ] Implements interfaces defined in the domain layer (e.g., repositories, services, event handlers)
- [ ] Handles all external system interactions (databases, message queues, external APIs, file systems)
- [ ] Contains data persistence implementations (ORM configurations, database migrations, query builders)
- [ ] Manages cross-cutting concerns (logging, security, caching, monitoring)
- [ ] Converts between domain objects and external data formats (DTOs, API responses)
- [ ] Infrastructure-specific exceptions are caught and translated to domain exceptions
- [ ] Technical details are encapsulated and not exposed to higher layers

### Repository Pattern
- [ ] Domain repositories handle persistence without exposing implementation details
- [ ] Repositories work with domain objects, not DTOs or ORM models
- [ ] Query objects or specifications used for complex queries
- [ ] N/A - This PR doesn't involve backend domain logic

## Testing Performed
<!-- Describe the testing you've done to verify your changes -->
- [ ] Added unit tests
- [ ] Manually tested all scenarios
- [ ] Verified in development environment

## Screenshots/Recordings (if appropriate)
<!-- Add screenshots or recordings demonstrating the change -->

## Self-Review Checklist
<!-- Mark with an 'x' all that apply -->
- [ ] My code follows the project's style guidelines
- [ ] I have used a linter during development (mandatory for Python and TypeScript)
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings or errors
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass with my changes
- [ ] I have confirmed my PR does NOT include migration files
- [ ] I have completed the Change Narrative section with a clear explanation of my implementation approach and decisions
- [ ] I have documented all development decisions (architecture, code, library choices, trade-offs) in an ADR in the docs/architecture folder

## Billify Development Workflow Compliance
<!-- Ensure your PR follows Billify's development guidelines -->
- [ ] This PR addresses a single Linear ticket/feature (or closely related tickets that form a cohesive unit)
- [ ] I've used a properly named branch following the format: `feature/BIL-XX-brief-description` or `bugfix/BIL-XX-brief-description`
- [ ] I've clearly documented which tickets are being addressed in this PR
- [ ] I have addressed all Code Rabbit review comments (mandatory before human review - use free trial if needed, regular contributors can request a seat)
- [ ] I understand this PR will remain "In Review" until approved
- [ ] I will promptly address reviewer feedback within 24-48 hours of receiving it

## PR Naming Guidelines
<!-- Make sure your PR title follows the format: "[BIL-XX] Brief description of changes" -->
<!-- For example: "[BIL-86] Implement Ponto API Authentication" -->

## Reviewer Guidelines
<!-- Instructions for reviewers -->
- Please review within 24-48 hours (our target)
- Check that the Change Narrative section is complete and actually helps understand the PR (PRs without a proper narrative should be returned)
- Focus on: [Specific areas that need careful review]
- Ensure the code maintains consistency with the rest of the codebase
- Verify DDD principles are properly applied (no mixed responsibilities, clear boundaries)
- Check that proper documentation and type hints are included
- Suggested testing approach: [any specific testing advice]
