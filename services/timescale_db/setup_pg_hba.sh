#!/bin/bash
set -e

# Copy custom pg_hba.conf to PostgreSQL data directory
echo "Setting up pg_hba.conf for network access..."
cp /docker-entrypoint-initdb.d/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf
chown postgres:postgres /var/lib/postgresql/data/pg_hba.conf
chmod 600 /var/lib/postgresql/data/pg_hba.conf

echo "pg_hba.conf configured successfully"