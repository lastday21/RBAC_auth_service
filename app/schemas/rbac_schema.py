from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    name: str = Field(min_length=1)


class RoleUpdate(BaseModel):
    name: str = Field(min_length=1)


class RoleOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ElementCreate(BaseModel):
    code: str = Field(min_length=1)
    title: str | None = None


class ElementUpdate(BaseModel):
    title: str | None = None


class ElementOut(BaseModel):
    id: int
    code: str
    title: str | None

    model_config = {"from_attributes": True}


class RuleUpsert(BaseModel):
    role_id: int
    element_id: int

    read_permission: bool = False
    read_all_permission: bool = False

    create_permission: bool = False

    update_permission: bool = False
    update_all_permission: bool = False

    delete_permission: bool = False
    delete_all_permission: bool = False


class RuleOut(BaseModel):
    id: int
    role_id: int
    element_id: int

    read_permission: bool
    read_all_permission: bool

    create_permission: bool

    update_permission: bool
    update_all_permission: bool

    delete_permission: bool
    delete_all_permission: bool

    model_config = {"from_attributes": True}
