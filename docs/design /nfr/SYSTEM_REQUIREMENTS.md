# System setup, servers and environment

## Web-based system

Billify should operate as a web-based application accessible through standard web browsers (Chrome, Firefox, Safari, Edge) on desktop and tablet (mobile optimisation post-MVP)

## Web server requirements

The web server deploying the Billify MVP **assuming 10 initial users** should meet the following requirements:
- Memory: 400MB RAM
    1. Django + dependencies ~200MB RAM
    2. Celery ~ 100MB RAM
    3. 1 minute sync ~ 100MB RAM
- CPU: basic, modern single threaded CPU as the load is very low
- Storage: 2GB (monthly)
    1. Django app + dependencies: ~500MB
    2. Logs: ~1GB/month
- Network inbound/outbound data: 4GB (monthly)
    1. API sync, JSON payload: 
        1. 100KB/sync → 144MB/day → 4GB/month

**A basic digital ocean droplet** with the following system specifications meets these initial requirements:
- 512MB RAM
- 1 virtual CPU, shared
- 500GB outbound data transfer/month
- 10GB SSD

Over time, the web server requirements will need to be scaled with more users and data.
- Digital ocean allows to resize droplets as the demands of the application increase.
- For a small user base (10-100 users) and a basic feature set, upgrading hardware is more cost-effective than spending developer time on optimisation:
    - Hardware costs are predictable and relatively low at this scale.
    - Developer time is expensive and could be better spent on features.
    - Early optimisation can be premature without real usage patterns.
    - Droplet upgrades are quick and straightforward.
- However, this approach has limits - at larger scales (1000+ users), optimisation becomes necessary as hardware costs grow exponentially.

## Database server requirements

The database server storing the Billify MVP data **assuming 10 initial users** should meet the following requirements:
- Memory: 1GB RAM
    - Base PostgreSQL ~100MB:
        - Core database process
        - System catalogs
        - Basic functionality
    - Connections ~100MB:
        - 10 MB memory space for each client connection
        - 10 connections with 10 users
    - Shared buffers ~256MB:
        - PostgreSQL's main cache
        - Stores recently accessed data
        - Table and index pages
        - Reduces disk I/O
        - Typically 25% of total RAM (assuming 1GB RAM)
    - Working memory ~64MB:
        - Memory for sorting operations
        - Used for ORDER BY, GROUP BY
        - Temporary space for query execution
        - Per operation allocation
- CPU: basic, modern single threaded CPU as the load is very low at 10 initial users
- Storage: 1GB/month
    - Database records with 10 users ~ 300MB/month
    - System needs ~ 700MB
        - PostgreSQL installation ~100MB
        - WAL logs ~500MB
        - Indexes (~30%) ~ 100MB/month

**A basic, regular digital ocean PostgreSQL database server** with the following system specifications meets these initial requirements:
- 1GB RAM
- 1vCPU
- 10GB disk space

Over time, the database server requirements will need to be scaled with more users and data.
- Digital ocean allows to scale up CPUs, RAM and storage at any time to support growth.

## Object storage requirements

The object storage requirements for the the Billify MVP **assuming 10 initial users** should meet the following requirements:
- File storage: 600MB (monthly)
- Upload/download of files: 1800MB (monthly)
    - 600MB/month uploads
    - 1.2GB/month downloads (assuming each file is accessed twice)

**One digital ocean spaces bucket** with the following specifications meet these initial requirements:
- 250GB storage
- 1TB outbound transfer