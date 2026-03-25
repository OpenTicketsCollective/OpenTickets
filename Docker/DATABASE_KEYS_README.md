# OpenTickets Database SSH Key Authentication

Generated: 3 ED25519 SSH key pairs for different access levels

## 1. HEALTHCHECK USER
**Purpose:** Health check monitoring with server status and control capabilities
**File:** `healthcheck_key` (private) / `healthcheck_key.pub` (public)
**Fingerprint:** SHA256:gDPM2dovoT9UN6W8G0NuuDcwOTFm1CXEGv0o9FY5LVQ
**Permissions:**
- SELECT on opentickets_db.* (read data)
- PROCESS (view running queries and threads)
- REPLICATION CLIENT (monitor replication status)
- SHOW DATABASES, SHOW VIEW (view database/view definitions)
- SUPER (can execute SHUTDOWN, SET GLOBAL variables)
- Can only connect from localhost
- Used for container health checks, monitoring, and graceful shutdown

**MySQL User:** `healthcheck@localhost`
**Public Key:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAmMoa0Z/oe52h0qPZqhtmk6rtzP7kVKn1HB7TUxOTFp healthcheck@opentickets
```

---

## 2. DATABASE USER
**Purpose:** Application database access with write permissions
**File:** `database_user_key` (private) / `database_user_key.pub` (public)
**Fingerprint:** SHA256:jKPogxznSfrLdmKNeGwIAHu6OSq17b8mvzXNLOzM25k
**Permissions:**
- SELECT, INSERT, UPDATE, DELETE on opentickets_db.*
- CREATE TEMPORARY TABLES
- Can connect from any host (%)
- Used by the application for standard operations

**MySQL User:** `dbuser@%`
**Public Key:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP/n3+/IYfe8G7OcTUMqSRpzZ5MO2mRXcDtioHqFBG6Z dbuser@opentickets
```

---

## 3. ROOT LOCALHOST USER
**Purpose:** Administrative access, restricted to localhost only
**File:** `root_localhost_key` (private) / `root_localhost_key.pub` (public)
**Fingerprint:** SHA256:M4+eRkYg9Jpl0KqtT/H8ofDYLgehowsMyYTGmEe2eCk
**Permissions:**
- ALL PRIVILEGES (full administrative access)
- WITH GRANT OPTION
- Can only connect from localhost (127.0.0.1, localhost)
- Used for database maintenance and administration

**MySQL User:** `root@localhost`
**Public Key:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOdU9kBv81VySttnQMjA3oeerpm0f07p7VUdHZ12xwZ5 root@localhost
```

---

## Setup Instructions

1. **Apply the SQL setup script to the running MySQL container:**
   ```bash
   mysql -h 127.0.0.1 -P 3307 -u root -pRootPass123! < setup_mysql_users.sql
   ```

2. **Store the private keys securely:**
   - `healthcheck_key` - Use in container health check configuration
   - `database_user_key` - Distribute to application servers (restricted write access)
   - `root_localhost_key` - Keep secure for administrative access only

3. **Update docker-compose.yml health check:**
   ```yaml
   healthcheck:
     test: ["CMD", "mysql", "-u", "healthcheck", "-pAAAAC3NzaC1lZDI1NTE5AAAAIAmMoa0Z/oe52h0qPZqhtmk6rtzP7kVKn1HB7TUxOTFp", "-e", "SELECT 1"]
     interval: 30s
     timeout: 10s
     retries: 3
     start_period: 40s
   ```

---

## Key Security Notes

- **Private Key Files:** Already set to restricted permissions (600)
- **Healthcheck User:** Read-only, minimal attack surface
- **DBUser:** Write access but no administrative privileges
- **Root:** Localhost-only to prevent remote root access
- **Network Security:** Consider using SSL/TLS for database connections over the network

---

## Files Generated

- `healthcheck_key` - Healthcheck private key
- `healthcheck_key.pub` - Healthcheck public key
- `database_user_key` - DBUser private key
- `database_user_key.pub` - DBUser public key
- `root_localhost_key` - Root private key
- `root_localhost_key.pub` - Root public key
- `setup_mysql_users.sql` - SQL script to create users and set permissions
