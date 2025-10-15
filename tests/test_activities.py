from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of participants to restore after each test
    original = {k: v["participants"][:] for k, v in activities.items()}
    yield
    for k, parts in original.items():
        activities[k]["participants"] = parts[:]


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    client = TestClient(app)
    activity = "Chess Club"
    email = "test_student@mergington.edu"

    # signup
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # duplicate signup should fail
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400

    # unregister
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_nonexistent_activity():
    client = TestClient(app)
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_unregister_not_signed_up():
    client = TestClient(app)
    activity = "Programming Class"
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": "not@there.com"})
    assert resp.status_code == 400
