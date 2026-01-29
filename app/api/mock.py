from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth_jwt import get_current_user
from app.core.rbac import has_all_permission, has_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.mock_schema import OrderOut, ProductOut, ProductPatch

mock_router = APIRouter(prefix="/mock", tags=["mock"])


def _build_products(current_user_id: int) -> list[dict]:
    other_user_id = current_user_id + 1
    items = []
    items.append({"id": 1, "title": "My product 1", "owner_id": current_user_id})
    items.append({"id": 2, "title": "Alien product", "owner_id": other_user_id})
    items.append({"id": 3, "title": "My product 2", "owner_id": current_user_id})
    return items


def _build_orders(current_user_id: int) -> list[dict]:
    other_user_id = current_user_id + 1
    items = []
    items.append({"id": 101, "status": "new", "owner_id": current_user_id})
    items.append({"id": 102, "status": "paid", "owner_id": other_user_id})
    items.append({"id": 103, "status": "shipped", "owner_id": current_user_id})
    return items


@mock_router.get("/products", response_model=list[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = _build_products(user.id)

    if has_all_permission(db, user, "products", "read"):
        return items

    if not has_permission(db, user, "products", "read", owner_id=user.id):
        raise HTTPException(status_code=403, detail="forbidden")

    result = []
    for item in items:
        if item["owner_id"] == user.id:
            result.append(item)

    return result


@mock_router.patch("/products/{product_id}", response_model=ProductOut)
def patch_product(
    product_id: int,
    payload: ProductPatch,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = _build_products(user.id)

    found_item = None
    for item in items:
        if item["id"] == product_id:
            found_item = item
            break

    if found_item is None:
        raise HTTPException(status_code=404, detail="not found")

    ok = has_permission(db, user, "products", "update", owner_id=found_item["owner_id"])
    if not ok:
        raise HTTPException(status_code=403, detail="forbidden")

    found_item["title"] = payload.title
    return found_item


@mock_router.get("/orders", response_model=list[OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items = _build_orders(user.id)

    if has_all_permission(db, user, "orders", "read"):
        return items

    if not has_permission(db, user, "orders", "read", owner_id=user.id):
        raise HTTPException(status_code=403, detail="forbidden")

    result = []
    for item in items:
        if item["owner_id"] == user.id:
            result.append(item)

    return result
