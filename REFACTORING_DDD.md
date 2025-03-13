# DDD Compliance Refactoring

This branch is dedicated to refactoring the Billify codebase to better align with Domain-Driven Design (DDD) principles.

## Purpose

The purpose of this refactoring is to:

1. Identify and document components that don't follow DDD principles
2. Create a clear roadmap for refactoring these components
3. Implement an incremental approach to migrating to a proper DDD architecture

## Identified Issues

See `docs/development/ddd_compliance_issues.md` for a detailed analysis of the non-compliant modules.

## Refactoring Approach

Rather than deleting non-compliant code immediately (which would break functionality), we're taking an incremental approach:

1. **Document**: Clearly document all non-compliant areas
2. **Plan**: Create targeted refactoring tickets for each component
3. **Implement**: Gradually migrate functionality to DDD-compliant structures
4. **Maintain**: Update standards and guidelines to prevent regression

## Next Steps

After this PR is merged, specific refactoring tickets should be created for each non-compliant module, with clear implementation plans that minimize disruption to ongoing development.

## Reference Architecture

The reference for our DDD architecture can be found in:
- `backend/backend-readme.md`
- `docs/development/decisions/domain_vs_django_models.md`
- `backend/domain/README.md`
- `backend/infrastructure/README.md` 