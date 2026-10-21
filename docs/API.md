# EventSphere API reference

Base URL: `http://127.0.0.1:8000` · Format: JSON · Live docs: `/docs`

Errors return `{"detail": "message"}` (validation errors return a list of field problems with status 422).

## Health

### `GET /`
Returns `{"message": "Welcome to EventSphere!", "status": "running"}`. The frontend's status pill uses it.

## Authentication

### `POST /auth/signup` → 201
```json
{ "name": "Jane Doe", "email": "jane@example.com", "password": "min8chars", "role": "participant" }
```
`role` is `participant` (default) or `organizer`. Password: 8–128 characters. Errors: **409** email already exists.

### `POST /auth/login`
```json
{ "email": "jane@example.com", "password": "min8chars", "role": "participant" }
```
Success: `{"message": "Login successful", "user": {"id", "name", "email", "role"}}`.
Errors: **401** wrong email/password · **403** account belongs to a different role.

## Events

Event object: `{ id, title, description, location, event_date, capacity }`. `event_date` is an ISO string such as `2026-11-05T18:30:00` or `null`.

| Method & path | Purpose | Notes |
|---|---|---|
| `POST /events` | Create an event (201) | Body below |
| `GET /events` | List events | `{message, total, events[]}` |
| `PUT /events/{id}` | Update an event | Same body as create. 404 if missing |
| `DELETE /events/{id}` | Delete an event | 404 if missing |

Create / update body:
```json
{
  "title": "Tech Meetup",          // 3–150 chars
  "description": "Optional text",
  "location": "Jaipur",            // 2–200 chars
  "event_date": "2026-11-05T18:30",
  "capacity": 100                  // > 0
}
```

### `GET /events/{id}/analytics`
```json
{ "event_id": 1, "event_title": "Tech Meetup", "capacity": 100,
  "total_registrations": 40, "checked_in": 12,
  "pending_count_in": 28, "available_seats": 60 }
```

## Registrations and tickets

### `POST /events/{event_id}/register` → 201
```json
{ "attendee_name": "Jane Doe", "attendee_email": "jane@example.com" }
```
Creates a registration with a unique `ticket_code` (UUID) and saves a QR image. Response `registration` contains `id, attendee_name, attendee_email, event_id, ticket_code, checked_in, qr_code_url` (e.g. `/qr_codes/ticket_5.png`; prefix with the base URL to load the image).
Errors: **404** event not found · **400** email already registered for this event · **400** event is full.

### `GET /events/{event_id}/registrations`
`{event_id, total_registrations, attendees: [{id, attendee_name, attendee_email, checked_in}]}`

### `DELETE /registrations/{registration_id}`
Cancels a registration. 404 if missing.

### `POST /registrations/check-in/{ticket_code}`
Marks the ticket as used. Success: `{message, attendee_name, event_id, checked_in: true}`.
Errors: **404** invalid ticket code · **400** ticket already checked in.

## Static files

`GET /qr_codes/ticket_{registration_id}.png` serves the generated QR image. The QR content is the plain `ticket_code`.

## Data model

| Table | Columns |
|---|---|
| `events` | id, title, description, location, event_date, capacity |
| `registrations` | id, attendee_name, attendee_email, event_id → events.id, ticket_code (unique), checked_in (0/1). Unique: (event_id, attendee_email) |
| `users` | id, name, email (unique), hashed_password, role |

Passwords are hashed with `pwdlib` (Argon2) and never returned.
