# Performance

## Response time
- System should maintain acceptable responsiveness for basic operations.
- Ensure system remains usable under normal load conditions. 
- Defer specific performance optimisation until post-MVP.

## Throughput
- Support basic operations for initial MVP user base (5-10 concurrent users)
- Handle basic file uploads up to 10MB per file.
- Process manual invoice uploads within reasonable timeframes
- Process integration data in batches, every minute.

### Sync operations
Each sync operation requires:
- Fetch all updated data every sync
   - Updates for all users are batched together, so one sync operation covers all users
- API calls to external systems (Yuki, Ponto)
   - 1440 sync operations per day
       → 1440 API calls to Yuki
       → 1440 API calls to Ponto
       → 2880 API calls in total

#### API rate limits and price
- Yuki:
   - 1000 calls/day (free)
   - 5000 calls/day (10euro/month)
   - 10000 calls/day (100euro/month)
- Ponto: Unknown rate limits and price. → Need to contact them.

#### Database operations
- READ operations (3-5 per sync):
   - Get last sync timestamp
   - Get list of connected integrations
   - Get existing invoices/transactions for deduplication
   - Get user settings and configurations
   → READ: 1,440 × 5 = 7,200 reads/day → 0.083 reads/second

- WRITE operations (2-20 per sync):
   - Store new invoices
   - Store new transactions
   - Update cash flow calculations
   - Update sync metadata
   - Log sync operation
   → WRITE: 1,440 × 10 = 14,400 writes/day (average case) → 0.167 writes/second

#### Data processing
- Estimated memory usage ~10MB/sync:
   - Not cumulative (garbage collected after each sync)
   - Typical data sizes:
       - JSON response: ~10-50KB per API
       - Parsed data: ~100-500KB in memory
       - Processing overhead: ~2-5MB
       - Total per sync: ~5-10MB memory

- Total estimated CPU processing time: **(HOW DID YOU CALCULATE THIS?)**
   - Best case (no new data): ~50ms
   - Average case (few updates): ~200ms
   - Worst case (many updates): ~500ms

- CPU utilisation per minute:
   - Best: 0.05s / 60s = 0.083% CPU time
   - Average: 0.2s / 60s = 0.33% CPU time
   - Worst: 0.5s / 60s = 0.83% CPU time

#### Storage updates
Each sync might update:
1. Database (PostgreSQL):
   - Estimated record data per sync: ~10KB in database storage, assuming:
       - 0-2 new invoices (one invoice record: ~1-2KB)
       - 0-5 new transactions (one transaction record: ~0.5-1KB)
       - 1 balance update, (one balance record: ~100 bytes)
       - 1 sync log (one sync log: ~200 bytes)
   - Total daily DB growth: 1MB, assuming:
       - Most syncs will find no new data
       - Let's say 100 new records per day:
           - 40 invoices: ~80KB
           - 60 transactions: ~60KB
           - 1,440 sync logs: ~576KB
           - Balance updates: ~288KB

2. Object storage (files, if any)
   - Estimated file data per sync ~1MB, assuming:
       - 0-2 new invoices (one invoice PDF, CSV, Excel: ~1MB)
   - Total daily object storage growth ~2MB, assuming:
       1. Most syncs will have no invoices attached to them.
       2. Let's say 2 new invoices per day (2MB) per user.
           1. 60 invoices per month (~60MB) per user.
           2. 720 invoices per year (~720MB) per user.