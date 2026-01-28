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


def _login(client, email: str, password: str = "123") -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_users_me_unauthorized_without_header(client):
    resp = client.get("/users/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "not authenticated"


def test_users_me_unauthorized_invalid_header(client):
    resp = client.get("/users/me", headers={"Authorization": "Basic abc"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "not authenticated"


def test_users_me_unauthorized_invalid_token(client):
    resp = client.get("/users/me", headers={"Authorization": "Bearer bad.token.value"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "not authenticated"


def test_users_me_ok_returns_profile(client):
    _register_user(client, email="me@test.com", full_name="Timur")
    token = _login(client, email="me@test.com")

    resp = client.get("/users/me", headers=_auth_headers(token))
    assert resp.status_code == 200

    data = resp.json()
    assert data["email"] == "me@test.com"
    assert data["full_name"] == "Timur"
    assert "password_hash" not in data


def test_users_me_patch_updates_full_name(client):
    _register_user(client, email="name@test.com", full_name="Timur")
    token = _login(client, email="name@test.com")

    resp = client.patch(
        "/users/me",
        headers=_auth_headers(token),
        json={"full_name": "Timur Updated"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Timur Updated"
    assert data["email"] == "name@test.com"


def test_users_me_patch_email_whitespace_returns_400(client):
    _register_user(client, email="space@test.com", full_name="Timur")
    token = _login(client, email="space@test.com")

    resp = client.patch(
        "/users/me",
        headers=_auth_headers(token),
        json={"email": "   "},
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "email must not be empty"


def test_users_me_patch_duplicate_email_returns_409(client):
    _register_user(client, email="dup1@test.com", full_name="User1")
    _register_user(client, email="dup2@test.com", full_name="User2")
    token = _login(client, email="dup2@test.com")

    resp = client.patch(
        "/users/me",
        headers=_auth_headers(token),
        json={"email": "dup1@test.com"},
    )
    assert resp.status_code == 409
    assert resp.json()["detail"] == "email already registered"


def test_users_me_patch_email_normalizes_to_lowercase(client):
    _register_user(client, email="norm@test.com", full_name="Timur")
    token = _login(client, email="norm@test.com")

    resp = client.patch(
        "/users/me",
        headers=_auth_headers(token),
        json={"email": "  NEW@TEST.COM  "},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "new@test.com"


def test_soft_delete_blocks_user(client):
    _register_user(client, email="timur@test.com", full_name="Timur")
    token = _login(client, email="timur@test.com")

    resp = client.delete("/users/me", headers=_auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    resp = client.get("/users/me", headers=_auth_headers(token))
    assert resp.status_code == 401
    assert resp.json()["detail"] == "not authenticated"
