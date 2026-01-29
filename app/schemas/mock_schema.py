from pydantic import BaseModel


class ProductOut(BaseModel):
    id: int
    title: str
    owner_id: int


class ProductPatch(BaseModel):
    title: str


class OrderOut(BaseModel):
    id: int
    status: str
    owner_id: int
