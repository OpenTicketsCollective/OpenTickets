# OpenTickets Frontend

Static frontend for the OpenTickets demo. No server required — open `index.html` in a browser.

Quick start:

```powershell
# from the Frontend directory
start index.html
```

Pages:
- `index.html` — public ticket submission form
- `staff.html` — staff login and dashboard (default staff users: `tech1` / `password`, `admin` / `password`)
- `ticket.html?id=<id>` — ticket detail and comments

Data is persisted to `localStorage` under the key `opentickets_db_v1` for demo purposes.
