from typing import Literal

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_jwt import get_current_user
from app.db.session import get_db
from app.models.access_role_rule import AccessRoleRule
from app.models.business_element import BusinessElement
from app.models.user import User
from app.models.user_role import UserRole

Action = Literal["read", "create", "update", "delete"]


def _raise_forbidden() -> None:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="forbidden",
    )


def has_permission(
    db: Session, user: User, resource: str, action: Action, owner_id: int | None = None
) -> bool:
    element = db.query(BusinessElement).filter(BusinessElement.code == resource).first()
    if not element:
        return False

    roles_id_rows = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    roles_id = [row.role_id for row in roles_id_rows]
    if not roles_id:
        return False

    rules = (
        db.query(AccessRoleRule)
        .filter(
            AccessRoleRule.role_id.in_(roles_id),
            AccessRoleRule.element_id == element.id,
        )
        .all()
    )
    if not rules:
        return False

    is_owner = owner_id is not None and user.id == owner_id

    for rule in rules:
        if action == "create" and rule.create_permission:
            return True

        if action == "read":
            if rule.read_all_permission:
                return True
            if is_owner and rule.read_permission:
                return True

        if action == "delete":
            if rule.delete_all_permission:
                return True
            if is_owner and rule.delete_permission:
                return True

        if action == "update":
            if rule.update_all_permission:
                return True
            if is_owner and rule.update_permission:
                return True

    return False


def require_permission(resource: str, action: Action):
    def check_permission(
        db: Session = Depends(get_db), user: User = Depends(get_current_user)
    ) -> User:
        if not has_permission(db=db, user=user, resource=resource, action=action):
            _raise_forbidden()
        return user

    return check_permission


def require_permission_with_owner(resource: str, action: Action):
    def check_permission(
        owner_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
    ) -> User:
        if not has_permission(
            db=db,
            user=user,
            resource=resource,
            action=action,
            owner_id=owner_id,
        ):
            _raise_forbidden()
        return user

    return check_permission
