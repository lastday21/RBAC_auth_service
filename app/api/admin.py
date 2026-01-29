from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.rbac import require_permission
from app.db.session import get_db
from app.models.access_role_rule import AccessRoleRule
from app.models.business_element import BusinessElement
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.rbac_schema import (
    ElementCreate,
    ElementOut,
    ElementUpdate,
    RoleCreate,
    RoleOut,
    RoleUpdate,
    RuleOut,
    RuleUpsert,
)

admin_router = APIRouter(prefix="/admin", tags=["admin"])


# ROLES
@admin_router.get(
    "/roles",
    response_model=list[RoleOut],
    dependencies=[Depends(require_permission("rbac_roles", "read"))],
)
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).order_by(Role.id).all()


@admin_router.post(
    "/roles",
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("rbac_roles", "create"))],
)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    role = Role(name=payload.name.strip())
    db.add(role)
    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="role already exists")
    return role


@admin_router.get(
    "/roles/{role_id}",
    response_model=RoleOut,
    dependencies=[Depends(require_permission("rbac_roles", "read"))],
)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="role not found")
    return role


@admin_router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("rbac_roles", "delete"))],
)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="role not found")

    db.delete(role)

    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="role is used")
    return None


@admin_router.patch(
    "/roles/{role_id}",
    response_model=RoleOut,
    dependencies=[Depends(require_permission("rbac_roles", "update"))],
)
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db)):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="role not found")

    role.name = payload.name.strip()

    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="role already exists")
    return role


# ELEMENTS


@admin_router.get(
    "/elements",
    response_model=list[ElementOut],
    dependencies=[Depends(require_permission("rbac_rules", "read"))],
)
def list_elements(db: Session = Depends(get_db)):
    return db.query(BusinessElement).order_by(BusinessElement.id).all()


@admin_router.post(
    "/elements",
    response_model=ElementOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("rbac_rules", "create"))],
)
def create_element(payload: ElementCreate, db: Session = Depends(get_db)):
    element = BusinessElement(code=payload.code.strip(), title=payload.title)
    db.add(element)
    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="element code already exists")
    return element


@admin_router.get(
    "/elements/{element_id}",
    response_model=ElementOut,
    dependencies=[Depends(require_permission("rbac_rules", "read"))],
)
def get_element(element_id: int, db: Session = Depends(get_db)):
    element = db.get(BusinessElement, element_id)
    if not element:
        raise HTTPException(status_code=404, detail="element not found")
    return element


@admin_router.delete(
    "/elements/{element_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("rbac_rules", "delete"))],
)
def delete_element(element_id: int, db: Session = Depends(get_db)):
    element = db.get(BusinessElement, element_id)
    if not element:
        raise HTTPException(status_code=404, detail="element not found")

    db.delete(element)
    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="element is used in rules")
    return None


@admin_router.patch(
    "/elements/{element_id}",
    response_model=ElementOut,
    dependencies=[Depends(require_permission("rbac_rules", "update"))],
)
def update_element(
    element_id: int, payload: ElementUpdate, db: Session = Depends(get_db)
):
    element = db.get(BusinessElement, element_id)
    if not element:
        raise HTTPException(status_code=404, detail="element not found")

    if payload.title is not None:
        element.title = payload.title

    db.add(element)
    db.flush()
    return element


# RULES


@admin_router.get(
    "/rules",
    response_model=list[RuleOut],
    dependencies=[Depends(require_permission("rbac_rules", "read"))],
)
def list_rules(
    db: Session = Depends(get_db),
    role_id: int | None = None,
    element_id: int | None = None,
):
    rules = db.query(AccessRoleRule)
    if role_id is not None:
        rules = rules.filter(AccessRoleRule.role_id == role_id)
    if element_id is not None:
        rules = rules.filter(AccessRoleRule.element_id == element_id)
    return rules.order_by(AccessRoleRule.id).all()


@admin_router.get(
    "/rules/{rule_id}",
    response_model=RuleOut,
    dependencies=[Depends(require_permission("rbac_rules", "read"))],
)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.get(AccessRoleRule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="rule not found")
    return rule


@admin_router.put(
    "/rules",
    response_model=RuleOut,
    dependencies=[Depends(require_permission("rbac_rules", "update"))],
)
def upsert_rule(payload: RuleUpsert, db: Session = Depends(get_db)):
    role = db.get(Role, payload.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="role not found")

    element = db.get(BusinessElement, payload.element_id)
    if not element:
        raise HTTPException(status_code=404, detail="element not found")

    rule = (
        db.query(AccessRoleRule)
        .filter(
            AccessRoleRule.role_id == payload.role_id,
            AccessRoleRule.element_id == payload.element_id,
        )
        .first()
    )
    if not rule:
        rule = AccessRoleRule(role_id=payload.role_id, element_id=payload.element_id)
        db.add(rule)

    rule.read_permission = payload.read_permission
    rule.read_all_permission = payload.read_all_permission
    rule.create_permission = payload.create_permission
    rule.update_permission = payload.update_permission
    rule.update_all_permission = payload.update_all_permission
    rule.delete_permission = payload.delete_permission
    rule.delete_all_permission = payload.delete_all_permission

    db.flush()
    return rule


# USER ROLES


@admin_router.get(
    "/users/{user_id}/roles",
    response_model=list[RoleOut],
    dependencies=[Depends(require_permission("rbac_user_roles", "read"))],
)
def list_user_roles(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    role_ids = db.query(UserRole.role_id).filter(UserRole.user_id == user_id).all()
    role_ids = [r[0] for r in role_ids]
    if not role_ids:
        return []

    return db.query(Role).filter(Role.id.in_(role_ids)).order_by(Role.id).all()


@admin_router.post(
    "/users/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("rbac_user_roles", "create"))],
)
def add_role_to_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="role not found")

    exists = (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
        .first()
    )
    if exists:
        return None

    db.add(UserRole(user_id=user_id, role_id=role_id))
    db.flush()
    return None


@admin_router.delete(
    "/users/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("rbac_user_roles", "delete"))],
)
def remove_role_from_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    link = (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
        .first()
    )
    if not link:
        return None

    db.delete(link)
    db.flush()
    return None
