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
