# OpenTickets

An open source IT ticket management system designed to be fully self-hostable.

![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/OpenTicketsCollective/OpenTickets)
![GitHub License](https://img.shields.io/github/license/OpenTicketsCollective/OpenTickets)

> [!IMPORTANT]
> This is an Alpha. Many features are not fully implimented or have bugs. (See [issues](https://github.com/OpenTicketsCollective/OpenTickets/issues)) I am actively working through the issue backlog. 
> I almost have all the know issues triaged and tracked in which case I will then work on better design docs and planning materials. PR's are welcome. Issues with ideas are also welcome. 
<img width="1914" height="1061" alt="image" src="https://github.com/user-attachments/assets/3ef4b53d-79a4-44a7-b378-448ba3a8d1cf" />

## Features

- Self-hostable IT ticket management system
- RESTful API backend with FastAPI
- Modern web frontend
- User authentication and authorization
- Ticket tracking and management
- Admin dashboard

## Prerequisites

### For Docker Deployment
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker CLI 
### For Local Development
- Python 3.12+ (Will move to python 3.15 soon but haven't tested yet)

## Quick Start

### Option 1: Docker Deployment (Recommended)

1. **Install Docker Desktop** from https://www.docker.com/products/docker-desktop/ or Docker CLI 

2. **Generate secrets** (from the project root):
   ```bash
   Docker\generate-secrets.sh
   ```

3. **Build and start the containers**:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. **Access the application**:
   - Hosted at: http://localhost or the manually set IP depending on configuration... Improvements to this system are pending. 

5. **Default test account**:
   - Email: `Admin@example.com`
   - Password: `AdminPass000!`

**To rebuild after making changes:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**View running containers:**
```bash
docker ps
```

> [!NOTE]
> The default test admin account will be replaced with a forced password reset on first login once that feature is fully implemented.
> See: [Issue #3](https://github.com/OpenTicketsCollective/OpenTickets/issues/3)

## Local Development

For local development, the Docker setup using nginx will handle localhost configuration automatically.
Docker is required at this stage.


## License
- AGPLv3
See [LICENSE](LICENSE) file for details.

## Support & Contribution

This is an open source project. Contributions are welcome!
