# ADR: Batch synchronization vs event-driven for MVP

## Status
Accepted

## Context
Need to choose between two approaches for keeping our system in sync with Yuki and Ponto:
1. Batch synchronization: Check for updates every minute
2. Event-driven: Get immediate updates when they happen

For detailed integration requirements, see [INTEGRATION.md](../../design%20/nfr/INTEGRATION.md).

## Decision
Implement batch synchronization with 1-minute intervals for MVP phase.

## Rationale

### Batch synchronization (chosen approach)
What it is:
- Simple scheduled task that runs every minute
- Directly calls Yuki and Ponto APIs to check for updates
- Each integration runs independently (Yuki failing won't affect Ponto)

Why we chose it:
1. **Simple to build and maintain**
   - Just a scheduled task making API calls
   - Basic error handling (retry next minute if fails)
   - Easy to monitor (clear success/failure)
   See [SYSTEM_ARCHITECTURE.md](../../architecture/SYSTEM_ARCHITECTURE.md#batch-sync-advantages) for details.

2. **Sufficient for MVP needs**
   - 1-minute delay acceptable for SMEs
   - Handles our target of 10-100 users
   - Works within free API limits (1000 calls/day)
   See [PERFORMANCE.md](../../design%20/nfr/PERFORMANCE.md#api-rate-limits-and-price) for API limits.

3. **Resource needs are clear**
   - 500ms processing time per user
   - 10MB memory per sync
   - Runs fine on basic server (512MB RAM, 1 CPU)
   See [SCALABILITY.md](../../design%20/nfr/SCALABILITY.md#server-specifications) for detailed metrics.

### Event-driven (considered but deferred)
What it is:
- System that gets immediate updates when data changes
- Uses a "post office" (message broker) to handle updates
- Needs extra infrastructure (RabbitMQ/Kafka)

Why we didn't choose it:
1. **Too complex for MVP**
   - Requires message queue setup
   - More complicated error handling
   - Harder to debug issues
   See [SYSTEM_ARCHITECTURE.md](../../architecture/SYSTEM_ARCHITECTURE.md#event-driven-requirements-deferred) for details.

2. **Not needed yet**
   - SMEs don't need real-time updates
   - 1-minute delay is acceptable
   - Extra complexity isn't justified
   See [AVAILABILITY.md](../../design%20/nfr/AVAILABILITY.md#estimated-usage-patterns) for usage patterns.

## Key constraints
- Initial target: 10 users (max 100)
- Belgium only, business hours (9AM-5PM)
- Web platform only
See [AVAILABILITY.md](../../design%20/nfr/AVAILABILITY.md#weekly-uptime-calculation) for business hours impact.

## Consequences

### Positive:
- Faster MVP development (aligns with launch early priority)
- Simple implementation:
  * Basic scheduled tasks
  * Clear error handling
  * Easy to debug and monitor
- Cost-effective for MVP:
  * Within Yuki free tier (1000 calls/day)
  * Single basic server (512MB RAM, 1 CPU)
  * No additional infrastructure needed
- Easy to maintain with clear success/failure states

For detailed cost analysis, see [PERFORMANCE.md](../../design%20/nfr/PERFORMANCE.md#api-rate-limits-and-price).

### Negative:
- Data freshness delay up to 1 minute (acceptable for MVP)
- Future real-time features will require:
  * Adding message queue infrastructure
  * Modifying sync logic
  * Updating monitoring
- Resource usage per user:
  * 500ms CPU time per sync
  * 10MB memory per sync
  * 10KB database storage
- Performance limitations at scale:
  * Max 100 users with current design
  * Need different approach beyond MVP scale

For detailed scaling analysis, see [SCALABILITY.md](../../design%20/nfr/SCALABILITY.md#scaling-limitations).

## Future considerations

### When to reconsider this decision

Only two factors would require switching to event-driven:
1. **Real-time updates become a business requirement**
   - Current 1-minute delay no longer acceptable
   - Customers specifically request immediate updates
   - Business case justifies the added complexity

2. **Technical limitations that can't be solved with hardware**
   - Note: Most scaling issues can be solved with hardware upgrades
   - Example: More users → More/better servers
   - Example: More API calls → Upgrade Yuki/Ponto tiers

For detailed upgrade paths, see [database_choice.md](database_choice.md#scaling-limitations-and-options).

### Performance optimization path
If performance issues arise:

1. **First: Hardware upgrades**
   - Increase RAM (currently 512MB)
   - Upgrade CPU
   - Scale vertically as needed
   See [SCALABILITY.md](../../design%20/nfr/SCALABILITY.md#ram-limitations) for RAM upgrade impact.

2. **Then: Software optimization**
   - Optimize database queries
   - Add caching where beneficial
   - Improve sync efficiency
   See [database_choice.md](database_choice.md#potential-optimizations) for options.

3. **Finally: Architecture changes**
   - Only if steps 1 and 2 insufficient
   - Only if real-time updates needed
   - Requires clear business justification 