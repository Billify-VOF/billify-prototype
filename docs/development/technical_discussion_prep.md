# Technical discussion preparation

## 1. Core architecture and design decisions

### 1.1 Domain-driven design approach

#### Why we chose DDD [Implemented - [ADR](decisions/domain_vs_django_models.md)]
- Clear separation between business logic and infrastructure [Implemented - Domain: [domain/models/](../../backend/domain/models/), Infrastructure: [infrastructure/django/models/](../../backend/infrastructure/django/models/)]
- Business logic explicit and aligned with stakeholder understanding [Implemented - [concepts/domain_modeling.md](concepts/domain_modeling.md)]

### 1.2 Database choice (PostgreSQL vs MongoDB)

#### Why PostgreSQL [Decision documented in [ADR](decisions/database_choice.md)]
Implementation status:
- Basic model structure [Implemented - [infrastructure/django/models/invoice.py](../../backend/infrastructure/django/models/invoice.py)]
- Data validation [Implemented - [api/views/invoice.py](../../backend/api/views/invoice.py)]
- Financial calculations [Planned - see [domain/README.md](../../backend/domain/README.md)]
- Transaction management [Not Implemented - see [database_choice.md](../development/decisions/database_choice.md)]

#### Scaling strategy [Analysis phase - [SCALABILITY.md](../design%20/nfr/SCALABILITY.md)]
Key considerations:
- Hardware limits identified and documented [see [SCALABILITY.md](../design%20/nfr/SCALABILITY.md)]
- Integration scaling strategy defined [see [INTEGRATION.md](../design%20/nfr/INTEGRATION.md)]
- Performance metrics established [see [PERFORMANCE.md](../design%20/nfr/PERFORMANCE.md)]


For detailed analysis of limitations and planned optimizations, see:
- [Scalability analysis](../design%20/nfr/SCALABILITY.md)
- [System architecture](../architecture/SYSTEM_ARCHITECTURE.md)
- [Performance requirements](../design%20/nfr/PERFORMANCE.md)

### 1.3 Design patterns

#### Current implementation status:
- Repository pattern for data access [Implemented - [infrastructure/django/repositories/](../../backend/infrastructure/django/repositories/)]
  - Complete implementation with domain conversion and standard operations
  - Examples: invoice_repository.py, cash_flow_repository.py

#### In progress:
- Adapter pattern for external services [In progress - [providers/](../../backend/integrations/providers/)]
  - Directory structure created
  - Implementation pending for Ponto and Yuki adapters

#### Planned patterns:
- Data transformation standardization [Planned - see [INTEGRATION.md](../design%20/nfr/INTEGRATION.md)]
  - Will standardize data formats across integrations
  - Common data model for invoices and transactions
  - Part of integration layer improvements
  - Structure created in [transformers/](../../backend/integrations/transformers/)

- Integration abstraction layer [Planned - see [SCALABILITY.md](../design%20/nfr/SCALABILITY.md)]
  - Standardized interface for all integrations
  - Each integration works on its own
  - Simplifies bug fixes and feature updates
  - Enables easy integration upgrades

  Benefits and trade-offs (from our documentation):
  1. Standardized interface [See [INTEGRATION.md](../design%20/nfr/INTEGRATION.md)]
     + Standardizes data formats (transactions, dates, status)
     + Ensures consistent field presence and types
     + Common model for invoices and transactions
     - Additional transformation layer needed
     - Must handle provider-specific features carefully

  2. Independent integrations [See [SCALABILITY.md](../design/nfr/SCALABILITY.md)]
     + Each service (Ponto, Yuki) works independently
     + If one service has issues, others keep working
     + Can add or remove services without breaking others
     - More complex when combining data from different services
     - Each service needs its own resources

#### Sync strategy
We chose batch synchronization (1-minute intervals) over event-driven architecture for MVP phase. This provides sufficient data freshness while maintaining simplicity.

For detailed analysis and rationale, see [sync strategy ADR](decisions/sync_strategy.md).

### 1.4 Technical architecture decisions

#### Architecture: monolith vs microservices
See our detailed analysis and decision in the [monolith vs microservices ADR](decisions/monolith_vs_microservices.md).

## 2. Production and operations

For production deployment details and considerations, see our [production readiness guide](../operations/production_readiness.md) and [enterprise deployment guide](../operations/enterprise_deployment.md).