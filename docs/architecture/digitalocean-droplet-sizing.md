# ADR: DigitalOcean Droplet Sizing for Billify Production Deployment

## Status

Implemented

## Date

2024-02-26

## Implementation Date

27 February 2025

## Context

The Billify application currently runs on a DigitalOcean droplet with 512 MB of RAM. This configuration needs to support multiple resource-intensive services:

- PostgreSQL database server
- Redis for caching and task queues
- Minio for S3-compatible object storage
- Django backend with Celery for background tasks
- Frontend application (React/Next.js)

According to the system requirements documentation, the initial sizing was designed for approximately 10 users:
- Web server: 400MB RAM (Django ~200MB, Celery ~100MB, Sync processes ~100MB)
- Database (PostgreSQL): 1GB RAM
- Object storage (Minio): Minimal RAM footprint for file operations

As noted in initial evaluation, 512 MB of RAM is insufficient to properly host all these services together, particularly due to:

1. PDF processing and OCR operations (using pytesseract and pdf2image) which are memory-intensive
2. Background tasks via Celery for integration syncing and data processing
3. Document storage and retrieval operations
4. Concurrent API requests and database operations

## Decision

Based on the system documentation and scalability analysis, we have upgraded the DigitalOcean droplet to accommodate the resource requirements of the Billify application.

### Implementation

The DigitalOcean droplet has been upsized to:
- 4GB RAM
- 2 vCPUs
- 10GB storage
- Cost: ~$24/month

This implemented option follows our "Recommended Option" from the initial proposal:
- Provides sufficient memory for up to ~75-100 users (per scalability analysis)
- The 2 vCPUs help with concurrent processing and PDF/OCR operations
- Suitable for moderate usage patterns with room for growth

## Resource Allocation Estimates

Based on the project documentation in `/docs/design/nfr/SYSTEM_REQUIREMENTS.md` and `/docs/design/nfr/SCALABILITY.md`:

| Service           | Estimated RAM Usage    | CPU Considerations                        |
|-------------------|------------------------|-------------------------------------------|
| PostgreSQL        | 150-250 MB             | Moderate for typical database operations  |
| Redis             | 50-100 MB              | Low to moderate                           |
| Minio             | 100-150 MB             | Moderate for file operations              |
| Django + Celery   | 300-400 MB             | High during PDF processing                |
| Frontend          | 100-150 MB             | Low to moderate                           |
| Sync Processes    | ~10MB per user per sync| Scales linearly with users                |
| OS + Overhead     | 100-200 MB             | Varies                                    |

According to the scalability documentation, memory usage scales approximately linearly with the number of users:
- ~10MB of RAM per user during synchronization
- With 512MB RAM (minus ~300MB for core services): Maximum ~20 users
- With 2GB RAM (minus ~300MB for core services): Maximum ~170 users
- CPU processing time of ~500ms per user per sync operation

## Alternative Considerations

Based on the project architecture documentation, we considered these alternatives:

1. **Split Services Approach**
   - Frontend: 1GB droplet
   - Backend + Celery: 2GB droplet
   - Managed PostgreSQL: DigitalOcean Managed Database (starting at $15/month)
   - Pros: Better isolation, independent scaling
   - Cons: Higher total cost, more complex configuration

2. **Managed Services Approach** (aligned with system architecture docs)
   - DigitalOcean Managed Postgres (from $15/month)
   - DigitalOcean Managed Redis (from $15/month)
   - DigitalOcean Spaces instead of Minio (from $5/month)
   - Small droplet for application logic (2GB, $12/month)
   - Pros: Reduced operational overhead, professional management
   - Cons: Higher total cost (~$47/month), potential vendor lock-in

3. **Mixed Approach** (recommended for growth beyond 100 users)
   - Application server: 2GB droplet ($12/month)
   - DigitalOcean Managed Postgres ($15/month)
   - Self-hosted Redis + Minio
   - Total cost: ~$27/month
   - Pros: Database reliability, reasonable cost, simpler scaling
   - Cons: Still managing some services yourself

## Rationale

The 4GB/2vCPU Standard Droplet is recommended as the best balance between:
- Cost efficiency
- Performance requirements
- User capacity (up to ~100 users per scalability analysis)
- Operational simplicity

This sizing accommodates Billify's specific requirements for PDF processing and OCR capabilities, which push the resource needs beyond a typical Django application. The system documentation clearly indicates that at the current 512MB RAM level, we can support only about 20 users max when considering memory requirements for sync operations.

## Consequences

### Positive

- Improved application performance
- More reliable service for users
- Capacity for growth from 10 to ~100 users with the recommended option
- Reduced risk of out-of-memory errors during PDF processing
- Better handling of concurrent sync operations

### Negative

- Increased hosting costs
- Potential for resource wastage in early stages of adoption

### Neutral

- Will require planning for a migration/upgrade from the current droplet
- May need to adjust sizing based on actual production usage patterns
- Should reassess when approaching 75-100 users based on performance metrics

## Implementation Plan

1. Create a new droplet with the selected specifications
2. Set up and configure all services on the new droplet:
   - Django backend with Celery
   - PostgreSQL (unless using managed services)
   - Redis for queues and caching
   - Minio for object storage
   - Nginx/frontend serving
3. Test thoroughly in a staging environment
4. Plan for minimal-downtime migration from current droplet
5. Monitor resource usage post-migration to validate sizing decision:
   - Memory usage during sync operations
   - CPU usage during PDF processing
   - Database performance

---

*Note: This recommendation is based on analysis of current codebase, documentation, and expected usage patterns. Per the scalability documentation, we should monitor actual resource usage and be prepared to optimize either through vertical scaling (larger droplet) or horizontal scaling (separate services) as the user base grows.* 