## OpenTickets
### An open source IT ticket management system designed to be fully self hostable.
> [!IMPORTANT]
> Opentickets is actively in development and while prereleases may be available they should not be used until a full release (Expected: Late April/Early May 2026). 

> [!NOTE]
> Development Status - Planning

Implemented Features 
- A proper Readme file... We gotta up these numbers

Installation
`TBD`

To start the backend server and the frontend connection you need to do these:
1. uvicorn backend:app --host 127.0.0.1 --port 8000 --reload

paste this in your browser to test the backend server functionality:
http://127.0.0.1:8000/docs

command to start the frontend server:
2. python -m http.server 5000

to test/see the page on a server run this in your browser:
http://127.0.0.1:5000/admin_page.html

note you do need to change the directory to all the way to openticket/backend for the backend server and opentickets/frontend for the frontend server
example: OpenTickets/tree/dev/env3/Backend
