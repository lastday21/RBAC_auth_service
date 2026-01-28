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


def test_users_me_unauthorized_without_header(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "not authenticated"


def test_users_me_unauthorized_invalid_header(client):
    resp = client.get("/users/me", headers={"X-User-Id": "abc"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "not authenticated"


def test_users_me_ok_returns_profile(client):
    user = _register_user(client, email="me@test.com", full_name="Timur")

    resp = client.get("/users/me", headers={"X-User-Id": str(user["id"])})
    assert resp.status_code == 200

    data = resp.json()
    assert data["id"] == user["id"]
    assert data["email"] == "me@test.com"
    assert data["full_name"] == "Timur"
    assert "password_hash" not in data


def test_users_me_patch_updates_full_name(client):
    user = _register_user(client, email="name@test.com", full_name="Timur")

    resp = client.patch(
        "/users/me",
        headers={"X-User-Id": str(user["id"])},
        json={"full_name": "Timur Updated"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Timur Updated"
    assert data["email"] == "name@test.com"


def test_users_me_patch_email_whitespace_returns_400(client):
    user = _register_user(client, email="space@test.com", full_name="Timur")

    resp = client.patch(
        "/users/me",
        headers={"X-User-Id": str(user["id"])},
        json={"email": "   "},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "email must not be empty"


def test_users_me_patch_duplicate_email_returns_409(client):
    _register_user(client, email="dup1@test.com", full_name="User1")
    second = _register_user(client, email="dup2@test.com", full_name="User2")

    resp = client.patch(
        "/users/me",
        headers={"X-User-Id": str(second["id"])},
        json={"email": "dup1@test.com"},
    )
    assert resp.status_code == 409
    assert resp.json()["detail"] == "email already registered"


def test_users_me_patch_email_normalizes_to_lowercase(client):
    user = _register_user(client, email="norm@test.com", full_name="Timur")

    resp = client.patch(
        "/users/me",
        headers={"X-User-Id": str(user["id"])},
        json={"email": "  NEW@TEST.COM  "},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "new@test.com"
