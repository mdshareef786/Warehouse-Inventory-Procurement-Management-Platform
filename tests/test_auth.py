def test_me_requires_authentication(client):
    response = client.get("/auth/me")

    assert response.status_code in (401, 403)


def test_me_rejects_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


def test_refresh_rejects_invalid_refresh_token(client):
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "invalid-refresh-token"
        }
    )

    assert response.status_code in (400, 401)


def test_logout_rejects_invalid_refresh_token(client):
    response = client.post(
        "/auth/logout",
        json={
            "refresh_token": "invalid-refresh-token"
        }
    )

    assert response.status_code in (400, 401)


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "definitely-not-a-real-user@example.com",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401


def test_register_validation_rejects_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "invalid-email",
            "password": "Password123!"
        }
    )

    assert response.status_code == 422


def test_register_validation_rejects_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 422