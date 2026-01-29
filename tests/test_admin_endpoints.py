from fastapi import status

from app.models.access_role_rule import AccessRoleRule
from app.models.business_element import BusinessElement
from app.models.role import Role
from app.models.user_role import UserRole


def _register_user(client, email: str, password: str = "123"):
    resp = client.post(
        "/auth/register",
        json={
            "full_name": "Test",
            "email": email,
            "password": password,
            "password_confirm": password,
        },
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    return resp.json()


def _login_token(client, email: str, password: str = "123") -> str:
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == status.HTTP_200_OK, resp.text
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _grant_admin_permissions(db_session, user_id: int):
    admin_role = Role(name="admin")
    db_session.add(admin_role)
    db_session.flush()

    db_session.add(UserRole(user_id=user_id, role_id=admin_role.id))
    db_session.flush()

    codes = ["rbac_roles", "rbac_rules", "rbac_user_roles"]
    for code in codes:
        element = BusinessElement(code=code, title=code)
        db_session.add(element)
        db_session.flush()

        rule = AccessRoleRule(
            role_id=admin_role.id,
            element_id=element.id,
            read_permission=True,
            read_all_permission=True,
            create_permission=True,
            update_permission=True,
            update_all_permission=True,
            delete_permission=True,
            delete_all_permission=True,
        )
        db_session.add(rule)

    db_session.flush()

    db_session.commit()


def test_admin_roles_requires_auth(client):
    resp = client.get("/admin/roles")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_admin_roles_forbidden_without_permission(client):
    _register_user(client, "user1@test.com")
    token = _login_token(client, "user1@test.com")

    resp = client.get("/admin/roles", headers=_auth_headers(token))
    assert resp.status_code == status.HTTP_403_FORBIDDEN


def test_admin_roles_crud_as_admin(client, db_session):
    admin = _register_user(client, "admin@test.com")
    _grant_admin_permissions(db_session, admin["id"])
    token = _login_token(client, "admin@test.com")
    h = _auth_headers(token)

    resp = client.post("/admin/roles", json={"name": "manager"}, headers=h)
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    role_id = resp.json()["id"]

    resp = client.get(f"/admin/roles/{role_id}", headers=h)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "manager"

    resp = client.patch(f"/admin/roles/{role_id}", json={"name": "manager2"}, headers=h)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "manager2"

    resp = client.delete(f"/admin/roles/{role_id}", headers=h)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    resp = client.get(f"/admin/roles/{role_id}", headers=h)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_admin_elements_crud_as_admin(client, db_session):
    admin = _register_user(client, "admin2@test.com")
    _grant_admin_permissions(db_session, admin["id"])
    token = _login_token(client, "admin2@test.com")
    h = _auth_headers(token)

    resp = client.post(
        "/admin/elements",
        json={"code": "demo_element", "title": "Demo"},
        headers=h,
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    element_id = resp.json()["id"]

    resp = client.get(f"/admin/elements/{element_id}", headers=h)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["code"] == "demo_element"

    resp = client.patch(
        f"/admin/elements/{element_id}",
        json={"title": "Demo2"},
        headers=h,
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["title"] == "Demo2"

    resp = client.delete(f"/admin/elements/{element_id}", headers=h)
    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_admin_rules_upsert_as_admin(client, db_session):
    admin = _register_user(client, "admin3@test.com")
    _grant_admin_permissions(db_session, admin["id"])
    token = _login_token(client, "admin3@test.com")
    h = _auth_headers(token)

    r = client.post("/admin/roles", json={"name": "viewer"}, headers=h)
    assert r.status_code == status.HTTP_201_CREATED
    role_id = r.json()["id"]

    e = client.post(
        "/admin/elements",
        json={"code": "reports", "title": "Reports"},
        headers=h,
    )
    assert e.status_code == status.HTTP_201_CREATED
    element_id = e.json()["id"]

    payload = {
        "role_id": role_id,
        "element_id": element_id,
        "read_permission": True,
        "read_all_permission": False,
        "create_permission": False,
        "update_permission": False,
        "update_all_permission": False,
        "delete_permission": False,
        "delete_all_permission": False,
    }
    resp = client.put("/admin/rules", json=payload, headers=h)
    assert resp.status_code == status.HTTP_200_OK, resp.text
    rule = resp.json()
    assert rule["role_id"] == role_id
    assert rule["element_id"] == element_id
    assert rule["read_permission"] is True

    resp = client.get(f"/admin/rules?role_id={role_id}", headers=h)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1


def test_admin_user_roles_assign_remove_as_admin(client, db_session):
    admin = _register_user(client, "admin4@test.com")
    _grant_admin_permissions(db_session, admin["id"])
    token = _login_token(client, "admin4@test.com")
    h = _auth_headers(token)

    target = _register_user(client, "target@test.com")
    r = client.post("/admin/roles", json={"name": "editor"}, headers=h)
    assert r.status_code == status.HTTP_201_CREATED
    role_id = r.json()["id"]

    resp = client.post(f"/admin/users/{target['id']}/roles/{role_id}", headers=h)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    resp = client.get(f"/admin/users/{target['id']}/roles", headers=h)
    assert resp.status_code == status.HTTP_200_OK
    names = [x["name"] for x in resp.json()]
    assert "editor" in names

    resp = client.delete(f"/admin/users/{target['id']}/roles/{role_id}", headers=h)
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    resp = client.get(f"/admin/users/{target['id']}/roles", headers=h)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == []
