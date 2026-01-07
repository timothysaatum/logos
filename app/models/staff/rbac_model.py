from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, Integer, String, Table, ForeignKey, Index, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.staff.user_model import User

# Association Tables
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("assigned_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("assigned_by", PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    Index("idx_user_roles_user", "user_id"),
    Index("idx_user_roles_role", "role_id"),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    Column("assigned_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Index("idx_role_perms_role", "role_id"),
    Index("idx_role_perms_perm", "permission_id"),
)


class Role(Base):
    """User roles for access control."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin"
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Role id={self.id} name='{self.name}'>"

    def has_permission(self, permission_name: str) -> bool:
        return any(p.name == permission_name for p in self.permissions)


class Permission(Base):
    """Granular permissions for actions."""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(96), unique=True, nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="noload"
    )

    __table_args__ = (
        Index("idx_permission_resource_action", "resource", "action", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Permission id={self.id} name='{self.name}'>"
