from sqlalchemy.orm import Session

from app.core.password import hash_password
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.access_role_rule import AccessRoleRule
from app.models.business_element import BusinessElement
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole


ADMIN_EMAIL = "admin@mail.ru"
ADMIN_PASSWORD = "admin123"
ADMIN_FULL_NAME = "Admin"

USER_EMAIL = "user@mail.ru"
USER_PASSWORD = "user123"
USER_FULL_NAME = "User"


def get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role:
        return role
    role = Role(name=name)
    db.add(role)
    db.flush()
    return role


def get_or_create_user(db: Session, email: str, full_name: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.is_active = True
        if user.full_name is None:
            user.full_name = full_name
            db.flush()
            return user

    user = User(
        email=email,
        full_name=full_name,
        password_hash=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_element(
    db: Session, code: str, title: str | None = None
) -> BusinessElement:
    element = db.query(BusinessElement).filter(BusinessElement.code == code).first()
    if element:
        if element.title is None:
            element.title = title
            db.add(element)
        return element

    element = BusinessElement(code=code, title=title)
    db.add(element)
    db.flush()
    return element


def get_or_update_rule(
    db: Session,
    role_id: int,
    element_id: int,
    *,
    read: bool,
    read_all: bool,
    create: bool,
    update: bool,
    update_all: bool,
    delete: bool,
    delete_all: bool,
) -> AccessRoleRule:
    rule = (
        db.query(AccessRoleRule)
        .filter(
            AccessRoleRule.role_id == role_id,
            AccessRoleRule.element_id == element_id,
        )
        .first()
    )

    if not rule:
        rule = AccessRoleRule(role_id=role_id, element_id=element_id)
        db.add(rule)

    rule.read_permission = read
    rule.read_all_permission = read_all
    rule.create_permission = create
    rule.update_permission = update
    rule.update_all_permission = update_all
    rule.delete_permission = delete
    rule.delete_all_permission = delete_all

    db.flush()
    return rule


def get_or_create_user_role(db: Session, user_id: int, role_id: int) -> None:
    link = (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
        .first()
    )
    if link:
        return

    db.add(UserRole(user_id=user_id, role_id=role_id))
    db.flush()


def seed_demo_data() -> None:
    init_db()

    with SessionLocal.begin() as db:
        admin_role = get_or_create_role(db, "admin")
        user_role = get_or_create_role(db, "user")

        admin = get_or_create_user(db, ADMIN_EMAIL, ADMIN_FULL_NAME, ADMIN_PASSWORD)
        user = get_or_create_user(db, USER_EMAIL, USER_FULL_NAME, USER_PASSWORD)

        get_or_create_user_role(db, admin.id, admin_role.id)
        get_or_create_user_role(db, user.id, user_role.id)

        elements = [
            ("rbac_roles", "Роли"),
            ("rbac_rules", "Правила доступа"),
            ("rbac_user_roles", "Роли пользователей"),
            ("products", "Товары"),
            ("orders", "Заказы"),
        ]

        element_objs = []
        for code, title in elements:
            element_objs.append(get_or_create_element(db, code=code, title=title))

        for element in element_objs:
            get_or_update_rule(
                db,
                role_id=admin_role.id,
                element_id=element.id,
                read=True,
                read_all=True,
                create=True,
                update=True,
                update_all=True,
                delete=True,
                delete_all=True,
            )

        elem_users = []
        for element in element_objs:
            if element.code in ["products", "orders"]:
                elem_users.append(element)

        for element in elem_users:
            get_or_update_rule(
                db,
                role_id=user_role.id,
                element_id=element.id,
                read=True,
                read_all=False,
                create=True,
                update=True,
                update_all=False,
                delete=True,
                delete_all=False,
            )

        print("Seed done!")
        print(f"Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"User:  {USER_EMAIL} / {USER_PASSWORD}")


if __name__ == "__main__":
    seed_demo_data()
