from app.models.access_role_rule import AccessRoleRule
from app.models.business_element import BusinessElement
from app.models.role import Role
from app.models.user_role import UserRole
from tests.conftest import TestingSessionLocal


def register_user_and_get_auth_headers(client, email: str, password: str = "123"):
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": email,
            "password": password,
            "password_confirm": password,
        },
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    return user_id, auth_headers


def grant_access_rule(
    user_id: int,
    role_name: str,
    element_code: str,
    **permissions,
):
    db = TestingSessionLocal()
    try:
        element = (
            db.query(BusinessElement)
            .filter(BusinessElement.code == element_code)
            .first()
        )
        if element is None:
            element = BusinessElement(code=element_code, title=element_code)
            db.add(element)
            db.flush()

        role = db.query(Role).filter(Role.name == role_name).first()
        if role is None:
            role = Role(name=role_name)
            db.add(role)
            db.flush()

        user_role_link = (
            db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role.id)
            .first()
        )
        if user_role_link is None:
            db.add(UserRole(user_id=user_id, role_id=role.id))
            db.flush()

        rule = (
            db.query(AccessRoleRule)
            .filter(
                AccessRoleRule.role_id == role.id,
                AccessRoleRule.element_id == element.id,
            )
            .first()
        )
        if rule is None:
            rule = AccessRoleRule(role_id=role.id, element_id=element.id)
            db.add(rule)
            db.flush()

        for key, value in permissions.items():
            setattr(rule, key, value)

        db.add(rule)
        db.commit()
    finally:
        db.close()


def test_mock_products_requires_authentication(client):
    response = client.get("/mock/products")
    assert response.status_code == 401
    assert response.json()["detail"] == "not authenticated"


def test_mock_products_with_token_but_no_rules_returns_403(client):
    _, auth_headers = register_user_and_get_auth_headers(client, "no_rules@test.com")

    response = client.get("/mock/products", headers=auth_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "forbidden"


def test_mock_products_read_own_returns_only_own_items(client):
    user_id, auth_headers = register_user_and_get_auth_headers(client, "user1@test.com")

    grant_access_rule(user_id, "user", "products", read_permission=True)

    response = client.get("/mock/products", headers=auth_headers)

    assert response.status_code == 200
    response_data = response.json()

    assert len(response_data) == 2
    for item in response_data:
        assert item["owner_id"] == user_id


def test_mock_products_read_all_returns_all_items(client):
    user_id, auth_headers = register_user_and_get_auth_headers(
        client, "admin1@test.com"
    )

    grant_access_rule(user_id, "admin", "products", read_all_permission=True)

    response = client.get("/mock/products", headers=auth_headers)

    assert response.status_code == 200
    response_data = response.json()

    assert len(response_data) == 3


def test_mock_patch_product_owner_can_update_own_product(client):
    user_id, auth_headers = register_user_and_get_auth_headers(client, "user2@test.com")

    grant_access_rule(user_id, "user", "products", update_permission=True)

    response = client.patch(
        "/mock/products/1",
        headers=auth_headers,
        json={"title": "Updated title"},
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["id"] == 1
    assert response_data["title"] == "Updated title"
    assert response_data["owner_id"] == user_id


def test_mock_patch_product_owner_cannot_update_alien_product(client):
    user_id, auth_headers = register_user_and_get_auth_headers(client, "user3@test.com")

    grant_access_rule(user_id, "user", "products", update_permission=True)

    response = client.patch(
        "/mock/products/2",
        headers=auth_headers,
        json={"title": "Hack"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "forbidden"


def test_mock_patch_product_admin_can_update_alien_product(client):
    user_id, auth_headers = register_user_and_get_auth_headers(
        client, "admin2@test.com"
    )

    grant_access_rule(user_id, "admin", "products", update_all_permission=True)

    response = client.patch(
        "/mock/products/2",
        headers=auth_headers,
        json={"title": "Admin updated"},
    )

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["id"] == 2
    assert response_data["title"] == "Admin updated"


def test_mock_orders_read_own_returns_only_own_items(client):
    user_id, auth_headers = register_user_and_get_auth_headers(client, "user4@test.com")

    grant_access_rule(user_id, "user", "orders", read_permission=True)

    response = client.get("/mock/orders", headers=auth_headers)

    assert response.status_code == 200
    response_data = response.json()

    assert len(response_data) == 2
    for item in response_data:
        assert item["owner_id"] == user_id
