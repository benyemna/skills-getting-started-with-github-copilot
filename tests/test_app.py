"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Test retrieving activities"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Chess Club",
            "Soccer Team",
            "Basketball Club",
            "Art Club",
            "Drama Society",
            "Math Club",
            "Science Olympiad",
            "Programming Class",
            "Gym Class",
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)


class TestSignup:
    """Test signing up for activities"""

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert "test@mergington.edu" in response.json()["message"]

    def test_signup_for_nonexistent_activity_returns_404(self):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email_returns_400(self):
        """Test that duplicate signup returns 400"""
        email = "duplicate@mergington.edu"
        # First signup
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200

        # Duplicate signup
        response2 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()

    def test_signup_updates_participant_list(self):
        """Test that signup updates the participant list"""
        email = "newparticipant@mergington.edu"
        activity_name = "Basketball Club"

        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])

        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Get updated participant count
        response = client.get("/activities")
        updated_count = len(response.json()[activity_name]["participants"])

        assert updated_count == initial_count + 1
        assert email in response.json()[activity_name]["participants"]


class TestUnregister:
    """Test unregistering from activities"""

    def test_unregister_success(self):
        """Test successful unregister from an activity"""
        email = "unreg@mergington.edu"
        activity_name = "Soccer Team"

        # First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Unregister
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in response.json()["message"]

    def test_unregister_from_nonexistent_activity_returns_404(self):
        """Test unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_non_participant_returns_400(self):
        """Test unregister of non-participant returns 400"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_removes_from_participant_list(self):
        """Test that unregister removes participant from list"""
        email = "removetest@mergington.edu"
        activity_name = "Art Club"

        # Sign up
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]

        # Unregister
        client.post(f"/activities/{activity_name}/unregister?email={email}")

        # Verify removal
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]


class TestRoot:
    """Test root endpoint"""

    def test_root_redirects(self):
        """Test that root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
