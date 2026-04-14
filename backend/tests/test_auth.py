import pytest


class TestRegister:
    def test_register_success(self, client, db):
        resp = client.post("/auth/register", json={
            "email": "new@example.com",
            "password": "SecurePass1!",
            "name": "Test User",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self, client, sample_user, db):
        resp = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass1!",
            "name": "Dup User",
        })
        assert resp.status_code == 409

    def test_register_weak_password(self, client, db):
        resp = client.post("/auth/register", json={
            "email": "weak@example.com",
            "password": "short",
            "name": "Weak",
        })
        assert resp.status_code == 400

    def test_register_invalid_email(self, client, db):
        resp = client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "SecurePass1!",
            "name": "Invalid",
        })
        assert resp.status_code == 400


class TestLogin:
    def test_login_success(self, client, sample_user, db):
        sample_user.email_verified = True
        db.session.flush()
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(self, client, sample_user, db):
        sample_user.email_verified = True
        db.session.flush()
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPass123!",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client, db):
        resp = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "Anything1!",
        })
        assert resp.status_code == 401

    def test_account_lockout(self, client, sample_user, db):
        sample_user.email_verified = True
        db.session.flush()
        for _ in range(5):
            client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "WrongPass123!",
            })
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        assert resp.status_code == 423


class TestProfile:
    def test_get_profile(self, client, auth_headers, db):
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert "email" in resp.get_json()

    def test_get_profile_unauthorized(self, client, db):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_update_profile(self, client, auth_headers, db):
        resp = client.put("/auth/me", headers=auth_headers, json={
            "name": "Updated Name",
        })
        assert resp.status_code == 200
