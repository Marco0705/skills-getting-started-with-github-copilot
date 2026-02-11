import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # snapshot activities and restore after each test to keep tests isolated
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(orig)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_duplicate():
    email = "testuser@example.com"
    activity = "Chess Club"

    # ensure not already present
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]

    # sign up
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # duplicate signup should fail
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400


def test_remove_participant():
    email = "removeme@example.com"
    activity = "Tennis Club"

    # sign up first
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200

    # now remove
    r = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r.status_code == 200
    assert "Removed" in r.json().get("message", "")

    # confirm removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]
