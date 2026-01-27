def test_register_ok(client):
    payload = {
        "full_name": "Timur",
        "email": "ok@test.com",
        "password": "123",
        "password_confirm": "123",
    }

    resp = client.post("/auth/register", json=payload)

    assert resp.status_code == 201

    data = resp.json()
    assert "id" in data
    assert data["email"] == "ok@test.com"
    assert data["full_name"] == "Timur"
    assert data["is_active"] is True
    assert "password_hash" not in data


def test_register_passwords_do_not_match(client):
    payload = {
        "full_name": "Timur",
        "email": "mismatch@test.com",
        "password": "123",
        "password_confirm": "999",
    }

    resp = client.post("/auth/register", json=payload)

    assert resp.status_code == 400
    assert resp.json()["detail"] == "passwords do not match"


def test_register_duplicate_email(client):
    payload = {
        "full_name": "Timur",
        "email": "dup@test.com",
        "password": "123",
        "password_confirm": "123",
    }

    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409
    assert second.json()["detail"] == "email already registered"
