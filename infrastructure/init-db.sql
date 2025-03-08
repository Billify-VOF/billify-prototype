DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'billify') THEN
        CREATE DATABASE billify;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'billify') THEN
        CREATE USER billify WITH PASSWORD 'billify_local';
    END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE billify TO billify;