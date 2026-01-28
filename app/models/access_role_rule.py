from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AccessRoleRule(Base):
    __tablename__ = "access_roles_rules"

    __table_args__ = (
        UniqueConstraint(
            "role_id", "element_id", name="uq_access_role_rule_role_element"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id"), nullable=False, index=True
    )
    element_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("business_elements.id"), nullable=False, index=True
    )

    read_permission: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    read_all_permission: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )

    create_permission: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )

    update_permission: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    update_all_permission: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )

    delete_permission: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    delete_all_permission: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
