import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_available_activities():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert activity_name in data
    assert "description" in data[activity_name]
    assert "participants" in data[activity_name]


def test_signup_adds_new_participant_to_activity():
    # Arrange
    activity_name = "Chess Club"
    new_email = "alex@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(url, params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}

    activities_response = client.get("/activities").json()
    assert new_email in activities_response[activity_name]["participants"]


def test_signup_duplicate_participant_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(url, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_removes_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "daniel@mergington.edu"
    url = f"/activities/{quote(activity_name)}/participants"

    # Act
    response = client.delete(url, params={"email": email_to_remove})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email_to_remove} from {activity_name}"}

    activities_response = client.get("/activities").json()
    assert email_to_remove not in activities_response[activity_name]["participants"]
