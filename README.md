# EventSphere

An event management app. Organizers publish events and check attendees in with a QR scanner; participants browse events, register and receive a QR ticket.

- **Backend:** FastAPI + SQLAlchemy (SQLite locally, PostgreSQL in deployment)
- **Frontend:** plain HTML, CSS and JavaScript with a white glassmorphism design (no build step)

## Features

| Role | What they can do |
|---|---|
| Visitor | See the home page with live events, dates and details |
| Participant | Sign up / log in, view event details, register, get a QR ticket, cancel a registration |
| Organizer | Create, edit and delete events (with date and time), view attendees and analytics, remove attendees, check in tickets by QR scan, image upload or typed code |

## Recommended folder structure

```
EventSphere/
├── README.md
├── docs/                      ← these documents
├── backend/
│   ├── main.py                ← API routes
│   ├── models.py              ← database tables
│   ├── schemas.py             ← request validation
│   ├── database.py            ← engine + session
│   ├── create_tables.py       ← optional: create tables manually
│   ├── migrate_database.py    ← optional: old SQLite migration helper
│   ├── requirements.txt
│   ├── .env                   ← optional: DATABASE_URL
│   ├── eventsphere.db         ← SQLite file (created automatically)
│   └── qr_codes/              ← generated ticket QR images
└── frontend/
    ├── index.html             ← home page
    ├── app.html               ← login, events, tickets, organizer tools
    ├── css/  style.css, home.css
    └── js/   api.js, app.js, home.js, jsQR.js
```

## Quick start

**1. Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn main:app --reload      # http://127.0.0.1:8000
```
Interactive API docs are available at <http://127.0.0.1:8000/docs>.

**2. Frontend**

Serve the `frontend` folder on **port 5500** (for example the VS Code *Live Server* extension, or `python -m http.server 5500` inside `frontend`). Then open <http://127.0.0.1:5500/index.html>.

Port 5500 matters: the backend's CORS list only allows `http://127.0.0.1:5500` and `http://localhost:5500`. To use another port or domain, add it to `allow_origins` in `backend/main.py`.

**3. Backend URL**

The frontend assumes the API is at `http://127.0.0.1:8000`. Click the status pill in the header (● online / ● offline) to change it; the value is saved in the browser.

## Configuration

| Setting | Where | Default |
|---|---|---|
| Database | `DATABASE_URL` in `backend/.env` | `sqlite:///./eventsphere.db` |
| Allowed origins (CORS) | `allow_origins` in `main.py` | ports 5500 on `127.0.0.1` and `localhost` |
| Backend URL for the frontend | status pill in the header | `http://127.0.0.1:8000` |

PostgreSQL example: `DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/eventsphere`

## Database upgrades

On startup `main.py` creates missing tables and adds the `users.role` and `events.event_date` columns to existing databases automatically. Restart the server after updating the code.

## Further reading

- [API reference](docs/API.md)
- [User guide and scanner testing](docs/USER_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Known limitations

- **No session tokens.** Login returns the user object and the frontend keeps it in the browser. The organizer-only endpoints (create/edit/delete event, check-in, view attendees) are not protected on the server, so the role split is only enforced in the UI. Add JWT authentication before a real deployment.
- **Deleting an event on SQLite** may leave its registrations behind, because SQLite does not enforce foreign-key cascades unless enabled.
- **"My Tickets"** is stored in the participant's browser, since the API has no endpoint that lists a user's registrations.
- **Registration is not tied to the logged-in account.** Anyone can register any name and email.
