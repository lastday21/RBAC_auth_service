def _register_user(client, email: str, full_name: str = "Timur"):
    payload = {
        "full_name": full_name,
        "email": email,
        "password": "123",
        "password_confirm": "123",
    }
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    return resp.json()


def test_login_ok_returns_token(client):
    _register_user(client, email="login@test.com")

    resp = client.post(
        "/auth/login", json={"email": "login@test.com", "password": "123"}
    )
    assert resp.status_code == 200

    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert data["access_token"].count(".") == 2


def test_login_wrong_password_returns_401(client):
    _register_user(client, email="wrong@test.com")

    resp = client.post(
        "/auth/login", json={"email": "wrong@test.com", "password": "bad"}
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "invalid credentials"


def test_login_unknown_email_returns_401(client):
    resp = client.post("/auth/login", json={"email": "no@test.com", "password": "123"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "invalid credentials"
