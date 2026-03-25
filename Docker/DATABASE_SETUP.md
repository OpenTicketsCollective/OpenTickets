# OpenTickets Database Setup Guide

## Quick Start

1. **Copy the environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Start the database container:**
   ```bash
   docker compose up -d
   ```

3. **Wait for the container to be healthy:**
   ```bash
   docker compose ps
   ```
   Wait until the `mysql` service shows `healthy` status.

4. **Create additional database users (optional but recommended):**
   ```bash
   docker compose exec mysql mysql -u root -p$MYSQL_ROOT_PASSWORD opentickets_db < setup_mysql_users.sql
   ```

---

## Image Information

This uses **Docker Hardened Images (DHI)** for enhanced security:
- Base Image: `dhi/mysql:8.4.8-debian13`
- Security Profile: CIS compliance
- End of Life: 2032-04-30
- Documentation: https://docs.docker.com/dhi/

---

## Default Credentials (Fresh Install)

### Root User
- **Username:** `root`
- **Password:** Set via `MYSQL_ROOT_PASSWORD` environment variable (default: `RootPass123!`)
- **Host:** `localhost` and `%` (initially)
- **Access:** Full administrative privileges

### Database
- **Name:** `opentickets_db`
- **Port:** 3306 (inside container), 3307 (mapped to host)

---

## Additional Database Users (After Initial Setup)

After running `setup_mysql_users.sql`, three additional users are created:

### 1. Healthcheck User
- **Username:** `healthcheck`
- **Password:** `AAAAC3NzaC1lZDI1NTE5AAAAIAmMoa0Z/oe52h0qPZqhtmk6rtzP7kVKn1HB7TUxOTFp`
- **Host:** `localhost`
- **Permissions:** SELECT, PROCESS, REPLICATION CLIENT, SUPER, SHOW DATABASES
- **Purpose:** Monitor database health and status

### 2. Application User
- **Username:** `dbuser`
- **Password:** `AAAAC3NzaC1lZDI1NTE5AAAAIP/n3+/IYfe8G7OcTUMqSRpzZ5MO2mRXcDtioHqFBG6Z`
- **Host:** `%` (any host)
- **Permissions:** SELECT, INSERT, UPDATE, DELETE, CREATE TEMPORARY TABLES
- **Purpose:** Application read/write access

### 3. Root Localhost User
- **Username:** `root`
- **Password:** `AAAAC3NzaC1lZDI1NTE5AAAAIOdU9kBv81VySttnQMjA3oeerpm0f07p7VUdHZ12xwZ5`
- **Host:** `localhost`
- **Permissions:** ALL PRIVILEGES
- **Purpose:** Local administrative access

---

## Connecting to the Database

### From Host Machine
```bash
# Using root (initial setup)
mysql -h 127.0.0.1 -P 3307 -u root -pRootPass123!

# Using application user
mysql -h 127.0.0.1 -P 3307 -u dbuser -pAAAAC3NzaC1lZDI1NTE5AAAAIP/n3+/IYfe8G7OcTUMqSRpzZ5MO2mRXcDtioHqFBG6Z
```

### From Application Container (Docker Compose)
```bash
# Using container DNS name
mysql -h mysql -u dbuser -pAAAAC3NzaC1lZDI1NTE5AAAAIP/n3+/IYfe8G7OcTUMqSRpzZ5MO2mRXcDtioHqFBG6Z opentickets_db
```

### Python Connector Example
```python
import mysql.connector

conn = mysql.connector.connect(
    host='mysql',  # Use 'localhost' or '127.0.0.1' if outside compose network
    user='dbuser',
    password='AAAAC3NzaC1lZDI1NTE5AAAAIP/n3+/IYfe8G7OcTUMqSRpzZ5MO2mRXcDtioHqFBG6Z',
    database='opentickets_db'
)
```

---

## Database Schema

The database automatically initializes with the following tables in `opentickets_db`:
- `User` - User accounts with authentication and access levels (Admin, L1, L2, User)
- `ActiveTickets` - Support tickets with status (Open, Closed, Error, Re-opened, Pending) and priority
- `Sessions` - User session management with tokens and expiration
- `TicketComments` - Comments on tickets with flagged URL detection
- `TicketAttachments` - File attachments to comments with MD5 checksums

---

## Useful Commands

```bash
# View container logs
docker compose logs -f mysql

# Connect to database interactively
docker compose exec mysql mysql -u root -pRootPass123!

# Check container health
docker compose ps

# Backup database
docker compose exec mysql mysqldump -u root -pRootPass123! opentickets_db > backup.sql

# Restore database
docker compose exec -T mysql mysql -u root -pRootPass123! opentickets_db < backup.sql

# Stop and remove containers
docker compose down
```

---

## Troubleshooting

### Container won't start
- Check environment variables are set: `docker compose config`
- View logs: `docker compose logs mysql`
- Verify volume permissions: `docker volume ls`

### Health check failing
- Ensure root password is correct in `docker-compose.yml`
- Check MySQL is fully initialized (wait 40+ seconds after start)
- View health check logs: `docker compose logs mysql`

### Connection refused
- Verify container is running: `docker compose ps`
- Check port mapping: `docker compose port mysql 3306`
- Ensure firewall allows port 3307 on host

### Access denied errors
- Verify username/password combination
- Check hostname/host filter (% allows any, localhost is restricted)
- Run `setup_mysql_users.sql` to create additional users
