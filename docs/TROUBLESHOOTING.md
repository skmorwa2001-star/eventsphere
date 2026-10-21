# Troubleshooting

| Problem | Cause and fix |
|---|---|
| Status pill shows **● offline** | Backend isn't running or the URL is wrong. Start `uvicorn main:app --reload`, or click the pill and enter the correct URL. |
| Browser console says *blocked by CORS policy* | The page isn't on port 5500. Serve the frontend on 5500, or add your origin to `allow_origins` in `main.py`. |
| `ModuleNotFoundError: pwdlib` | Run `pip install -r requirements.txt` (the updated file includes `pwdlib[argon2]`). |
| Server crashes at startup with *Directory 'qr_codes' does not exist* | Use the updated `main.py`, which creates the folder first, or create `backend/qr_codes/` manually. |
| Events show *Date to be announced* | They were created before dates existed. Edit the event and pick a date. |
| `no such column: events.event_date` | Use the updated `models.py` and `main.py` and restart the server; the column is added automatically. |
| Editing an event doesn't change capacity | That was a typo (`capcaity`) in the original `main.py`; fixed in the updated file. |
| Camera doesn't open in the scanner | Allow camera permission, use `127.0.0.1`/`localhost`/HTTPS, and close other apps using the webcam. |
| *No QR found* on image upload | Upload a clear image of just the ticket QR (use **⬇ Download QR**). Avoid blurry or heavily cropped screenshots. |
| QR image missing on the ticket | The backend must be reachable and `qr_codes/` must exist. Open `http://127.0.0.1:8000/qr_codes/ticket_1.png` to check. |
| *Invalid email or password* / *This account uses the organizer role* | Pick the same role you signed up with. |
| Tickets list is empty after switching browser | *My Tickets* is stored per browser. Organizers can still see all attendees under Manage. |
| Frontend still uses old data/URL | Hard refresh (Ctrl+F5). The backend URL is cached in the browser; click the status pill to change it. |
