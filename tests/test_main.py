from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to EventSphere!",
        "status": "running"
    }

def test_create_event():
    response=client.post(
        "/events",
        json={
            "title":"AI Workshop",
            "description":"Introduction to AI",
            "location":"Jaipur",
            "capacity":50
        }
    )
    print("STATUS:",response.status_code)
    print("BODY:",response.text)
    assert response.status_code==201

def test_create_event_invalid_capacity():
    response=client.post(
        "/events",
        json={
            "title":"AI Workshop",
            "description":"Introduction to AI",
            "location":"Jaipur",
            "capacity":0
        }
    )
    assert response.status_code==422


def test_update_event():
    # Step 1: Create an event first
    create_response = client.post(
        "/events",
        json={
            "title": "AI Workshop",
            "description": "Introduction to AI",
            "location": "Jaipur",
            "capacity": 50
        }
    )

    assert create_response.status_code == 201

    # Step 2: Get the event ID from the response
    event_id = create_response.json()["event"]

    # Step 3: Update the event
    response = client.put(
        f"/events/{event_id}",
        json={
            "title": "Updated AI Workshop",
            "description": "Updated workshop description",
            "location": "Jaipur",
            "capacity": 100
        }
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.text)

def test_delete_event():
    # Createe an event first
    create_response=client.post(
        "/events",
        json={
            "title":"Delete Test Event",
            "description":"Testing event deletion",
            "location":"Jaipur",
            "capacity":30
        }
    )
    assert create_response.status_code==201

    print("CREATE RESPONSE:",create_response.json())
    # get the created event id
    event_id=create_response.json()["event"]["id"]

    # delete thee event
    response=client.delete(f"/events/{event_id}")

    assert response.status_code==200
    assert response.json()["message"]=="Event deleted successfully"


def test_event_analytics():
    # create an event
    create_response=client.post(
        "/events",
        json={
            "title":"Analytics Test Event",
            "description":"Testing Analytics",
            "location":"Jaipur",
            "capacity":10
        }
    )
    assert create_response.status_code==201
    event_id=create_response.json()["event"]["id"]

    # check analystics for new event
    response=client.get(f"/events/{event_id}/analytics")

    assert response.status_code==200

    data=response.json()
    assert data["event_id"]==event_id
    assert data["total_registrations"]==0
    assert data["checked_in"]==0
    assert data["pending_count_in"]==0
    assert data["available_seats"]==10

    # Clean up
    delete_response=client.delete(f"/events/{event_id}")
    assert delete_response.status_code==200

def test_event_analytics_not_found():
    response=client.get("/events/999999/analytics")
    assert response.status_code==404    



def test_register_attendee():
    # Create a test event
    event_response = client.post(
        "/events",
        json={
            "title": "Registration Test Event",
            "description": "Testing attendee registration",
            "location": "Jaipur",
            "capacity": 5
        }
    )
    assert event_response.status_code == 201

    event_id = event_response.json()["event"]["id"]

    # Register an attendee
    response = client.post(
        f"/events/{event_id}/register",
        json={
            "attendee_name": "Test Attendee",
            "attendee_email": "attendee_test@example.com"
        }
    )

    assert response.status_code == 201

    data = response.json()
    assert data["registration"]["attendee_email"] == (
        "attendee_test@example.com"
    )
    assert data["registration"]["ticket_code"]

    # Clean up
    delete_response = client.delete(f"/events/{event_id}")
    assert delete_response.status_code == 200



def test_duplicate_registration():
    event_response = client.post(
        "/events",
        json={
            "title": "Duplicate Test Event",
            "description": "Testing duplicate registration",
            "location": "Jaipur",
            "capacity": 5
        }
    )
    assert event_response.status_code == 201

    event_id = event_response.json()["event"]["id"]

    attendee = {
        "attendee_name": "Duplicate Tester",
        "attendee_email": "duplicate_test@example.com"
    }

    # First registration should succeed
    first_response = client.post(
        f"/events/{event_id}/register",
        json=attendee
    )
    assert first_response.status_code == 201

    # Same email for the same event should be rejected
    second_response = client.post(
        f"/events/{event_id}/register",
        json=attendee
    )
    assert second_response.status_code == 400

    # Clean up the event
    delete_response = client.delete(f"/events/{event_id}")
    assert delete_response.status_code == 200


def test_check_in_invalid_ticket():
    response = client.post(
        "/registrations/check-in/invalid-ticket-code"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Invalid ticket code"



def test_successful_and_duplicate_check_in():
    # Create an event
    event_response = client.post(
        "/events",
        json={
            "title": "Check-in Test Event",
            "description": "Testing QR check-in",
            "location": "Jaipur",
            "capacity": 5
        }
    )
    assert event_response.status_code == 201
    event_id = event_response.json()["event"]["id"]

    # Register an attendee
    registration_response = client.post(
        f"/events/{event_id}/register",
        json={
            "attendee_name": "Checkin Tester",
            "attendee_email": "checkin_test@example.com"
        }
    )
    assert registration_response.status_code == 201

    ticket_code = registration_response.json()["registration"]["ticket_code"]

    # First check-in should succeed
    first_checkin = client.post(
        f"/registrations/check-in/{ticket_code}"
    )
    assert first_checkin.status_code == 200
    assert first_checkin.json()["checked_in"] is True

    # Second check-in should be rejected
    second_checkin = client.post(
        f"/registrations/check-in/{ticket_code}"
    )
    assert second_checkin.status_code == 400
    assert second_checkin.json()["detail"] == "Ticket already checked in"

    # Verify analytics
    analytics = client.get(f"/events/{event_id}/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["checked_in"] == 1

    # Clean up the event
    delete_response = client.delete(f"/events/{event_id}")
    assert delete_response.status_code == 200
