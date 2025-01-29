# Availability and reliability

## Uptime

### Estimated usage patterns
- Users check cash flow 1-2 times daily
- Invoice uploads few times weekly
- Access needed during business hours (9AM-5PM)
- Fallback options if system down:
 - Direct bank account access
 - Local invoice storage
 - Wait for system recovery

### Core requirements
1. Show cash flow position
2. Allow invoice uploads 
3. Sync with accounting software
  - Not time-critical for MVP
  - Data syncs on recovery

### Weekly uptime calculation

| Working days | Working hours | Weekly hours | % uptime | % downtime | Downtime hours |
|--------------|---------------|--------------|----------|------------|----------------|
| 5            | 8             | 40           | 90       | 10         | 4              |

#### Minimum requirements
- 90% uptime during business hours (9AM-5PM)
- Allowed downtime:
 - 4 hours/week during business hours for critical fixes
 - Unlimited outside business hours
 - Full weekends if needed
- Meets basic needs while minimizing complexity
- Upgradeable based on future needs

## Downtime management
- **Planned maintenance:** Outside business hours, weekends preferred
- **Critical fixes:** Immediate resolution during business hours
- **Unexpected issues:** Server/database problems during operation
- System status page for outage communication

## Data recovery

### Database recovery
Via Digital Ocean PostgreSQL:
- Daily backups
- 7-day retention period

### Object storage recovery
Via Digital Ocean SnapShooter:
- Automated backup solution
- [Documentation Link](https://docs.digitalocean.com/support/how-do-i-back-up-spaces-buckets/)

## Failover
- Automatic failover for database failures
- Standby replica node minimizes downtime
- Managed through Digital Ocean PostgreSQL service