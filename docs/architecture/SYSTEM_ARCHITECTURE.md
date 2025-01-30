# System architecture documentation

## Design, technical planning and architecture

The current design, technical planning, and architectural documentation should be viewed as a thoughtful but flexible starting point rather than a rigid blueprint.

While we've carefully considered our initial technical choices and system design based on current requirements and constraints, we fully expect this architecture to evolve as we begin building and learning from real-world usage.

The true value of this documentation lies not in its prescriptive details, but in providing a clear foundation that enables our team to start development with confidence while maintaining the agility to adapt.

As we build the MVP, we'll inevitably discover new challenges, gather user feedback, and gain insights that will reshape our understanding of both technical and business needs. This might lead us to refine our API design, adjust our data models, or even reconsider some of our initial technology choices.

## Core problem definition

Billify's fundamental purpose is to give SMEs a clear, real-time view of their cash flow position. The main pain points are:

- Fragmented financial data across multiple systems
- Difficulty in predicting and controlling cash flow
- Time-consuming manual processes
- Complex existing solutions requiring accounting expertise

## System architecture

![System architecture](/docs/architecture/diagrams/SystemArchitecture.png)

## Database relationships

```mermaid
erDiagram
    User ||--o{ Integration : has
    User ||--o{ Invoice : owns
    User ||--o{ Transaction : has
    User ||--o{ CashFlowPosition : tracks
    Invoice ||--o{ Transaction : matches
    Integration ||--o{ SyncLog : generates
```

## Key constraints & scope reductions

### User base constraints
- Initial target: 10 users
- Maximum MVP scale: ~100 users
- Geographic constraint: Belgium only
- Business hours only (9AM-5PM)
- Web platform only (defer mobile)

### Integration constraints
- Limit to only 2 critical integrations for MVP:
  - Yuki (accounting data)
  - Ponto (banking data)
- Defer other integrations (Exact, Billit, Silverfin) to post-MVP
- Simple polling-based sync (1-minute intervals) instead of real-time
- Read-only integration (no write-back to source systems)

### Technical stack

#### Frontend
- Single-page application using React
- Tailwind CSS for styling
- Basic charting with Recharts
- No mobile optimization needed

#### Backend
- Django (Python) monolith
- REST APIs for frontend communication
- Basic scheduled tasks with Celery
- Simple polling-based integration sync

#### Database
- Single PostgreSQL database
- Digital Ocean managed hosting
- Basic object storage for documents
- No need for complex caching initially

#### Infrastructure
- Digital Ocean basic droplet
- Managed PostgreSQL
- Single region (EU)
- Simple SSL/TLS security

#### Monitoring
- Basic error logging
- Simple uptime monitoring
- Essential security logging
- Basic performance metrics

## System requirements

### Web server requirements (10 users)
- Memory: 400MB RAM
  - Django + dependencies: 200MB
  - Celery: 100MB
  - Sync processes: 100MB
- CPU: single threaded (1 vCPU)
- Storage: 2GB monthly
  - Django app + dependencies: 500MB
  - Logs: 1GB/month
- Network: 4GB monthly
  - API sync payload: 100KB/sync → 144MB/day → 4GB/month

### Database server requirements
- Memory: 1GB RAM
  - Base PostgreSQL: 100MB
  - Connections (10MB × 10): 100MB
  - Shared buffers: 256MB
  - Working memory: 64MB
- Storage: 1GB/month
  - Database records: 300MB/month
  - System needs: 700MB
    - PostgreSQL installation: 100MB
    - WAL logs: 500MB
    - Indexes: 100MB/month

## Data models

The system uses several core entities to manage financial data and integrations:
- User: stores authentication and company information
- Integration: manages external system connections and sync state
- Invoice: tracks incoming and outgoing invoices
- Transaction: records actual money movements
- Cash flow position: represents point-in-time financial snapshots
- Sync log: monitors integration health and sync status

## Layered architecture

The system follows a layered architecture pattern to separate concerns and maintain flexibility:
- Presentation layer: handles user interface and API endpoints
- Application layer: coordinates business processes
- Domain layer: contains core business logic
- Integration layer: manages external system interactions
- Data layer: handles persistence and data access

## Failure points

### Web server failure
- **Impact**: application becomes completely inaccessible to users
- **Mitigation**:
  - Load balancer with multiple web server instances
  - Server monitoring with outage alerts
  - Auto-restart scripts

### File storage service failure
- **Impact**: users cannot upload or access stored files
- **Mitigation**:
  - Managed cloud storage (DigitalOcean Spaces/AWS S3)
  - File upload retry queue
  - Local metadata caching

### Service queue node failure
- **Impact**: delayed data syncs and report generation
- **Mitigation**:
  - Multiple queue nodes with failover
  - High-availability task broker (RabbitMQ/Redis)
  - Task retries and dead-letter queues

### Database server failure
- **Impact**: all data operations fail
- **Mitigation**:
  - Managed database with automatic failover
  - Read replicas
  - Regular backup testing
  - Query retry logic

## Containerization strategy

For MVP development, we use Docker to ensure environment consistency across development, testing, and production. Docker simplifies dependency management and deployment while maintaining scaling flexibility.

Kubernetes is intentionally excluded at this stage due to:
- Unnecessary operational complexity for single-developer MVP
- No immediate need for advanced container orchestration
- Focus on rapid iteration and value delivery

## Batch vs event-driven architecture

### Batch sync advantages
- Simple implementation and debugging
- Predictable resource usage
- 30-60 second delay acceptable for SME use case
- Easy monitoring and error handling

### Event-driven requirements (deferred)
- Message queue system
- Event store
- Complex retry mechanisms
- Webhook endpoints
- Event validation/ordering
- Deduplication logic

### Cost-benefit analysis

**Batch sync (30s/1min)**
- ✅ Simple implementation
- ✅ Easy maintenance
- ✅ Negligible resource usage
- ✅ Sufficient timeliness
- ✅ Simple error handling
- ✅ Simple monitoring
- ❌ Small data freshness delay

**Event-driven**
- ✅ Real-time updates
- ❌ Complex implementation
- ❌ Complex maintenance
- ❌ More infrastructure
- ❌ More points of failure
- ❌ Harder to debug
- ❌ Higher development cost

For MVP, batch synchronization provides the best balance of functionality and implementation complexity.