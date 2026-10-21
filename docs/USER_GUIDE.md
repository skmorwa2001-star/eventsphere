# EventSphere user guide

## Participants

1. Open the home page and click **Launch App** or **Get started**.
2. **Sign up**: choose *Participant*, enter name, email and a password of at least 8 characters. You are logged in right after signing up.
3. On **Events**, use **View details** to see the date, time, location, description and seats left.
4. Click **Register**. Your name and email are prefilled. A ticket with a QR code appears.
5. Use **⬇ Download QR** to save the ticket, or find it again under **My Tickets** (stored in this browser).
6. To cancel, go to **My Tickets** and click **Cancel**.

Show the QR code (on your phone or printed) to the organizer at the entrance.

## Organizers

1. Sign up or log in with the *Organizer* role.
2. **New Event**: title, description, date & time, location and capacity.
3. On each event card: **View details**, **Manage**, **Edit**, **Delete**.
4. **Manage** shows capacity, registered, checked in, pending and seats left, plus every attendee. **Remove** cancels an attendee's registration.
5. **Check-in** tab, three ways to check someone in:
   - **📷 Start scanner**: point the camera at the QR code.
   - **🖼️ Upload QR image**: choose a saved QR picture.
   - **Type the ticket code** and press *Check in*.

A green ✓ message means success. A red ✕ means an invalid code or a ticket that was already used.

## Testing the scanner on a laptop

1. Register as a participant and click **⬇ Download QR** (also copy the code shown under the QR).
2. Log out and log in as an organizer, then open **Check-in**.
3. Test with any of:
   - **Upload QR image**: pick the downloaded file (no camera needed).
   - **Webcam**: send the image to your phone and hold the phone in front of the webcam, or show a printed copy about 20–30 cm away.
   - **Typed code**: paste the ticket code.
4. Scan the same ticket again; it should show *Ticket already checked in*.

The camera only works on `localhost` / `127.0.0.1` or HTTPS pages, and the browser must be allowed to use it.

## Test checklist

- [ ] Sign up and log in as organizer and as participant
- [ ] Create an event with date and time, then edit it
- [ ] Register a participant; confirm the QR image appears
- [ ] Register the same email twice (should be rejected)
- [ ] Fill an event to capacity (next registration says *Event is full*)
- [ ] Check in a ticket; scan it again (should be rejected)
- [ ] Remove an attendee and watch seats-left update
- [ ] Delete an event
