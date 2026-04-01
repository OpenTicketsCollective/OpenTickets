# OpenTickets

An open source IT ticket management system designed to be fully self-hostable.

> [!IMPORTANT]
> OpenTickets is actively in development. While pre-releases may be available, they should not be used until a full release (Expected: Late April/Early May 2026).

> [!NOTE]
> **Development Status:** Planning

## Features

- A proper README file (more features coming soon)

## Installation

Coming soon.

## Getting Started

Before starting, ensure you navigate to the appropriate directories:
- **Backend:** `OpenTickets/Backend`
- **Frontend:** `OpenTickets/Frontend`

### Start the Backend Server

Navigate to the `Backend` directory and run:

```bash
python run_https.py
```

Then visit the API documentation in your browser:
```
http://127.0.0.1:8000/docs
```

### Start the Frontend Server

Navigate to the `Frontend` directory and run:

```bash
python -m http.server 5000
```

Then visit the admin page in your browser:
```
http://127.0.0.1:5000/admin_page.html
```
