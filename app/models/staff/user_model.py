from app.db import Base
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import String, Boolean, DateTime, Index, Text, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from app.models.staff.rbac import Role
    from app.models.laboratory.department_model import Department, Specialization
    from app.models.laboratory.branch_model import Branch


class User(Base):
    """Lab Staff model - works for any lab size."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    # Foreign key to branch (tenant isolation)
    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Authentication
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    staff_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    telephone: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    date_of_birth: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Employment
    employee_type: Mapped[str] = mapped_column(String(50), nullable=False, default="full_time")
    # full_time, part_time, contract, intern
    employment_status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    # active, on_leave, suspended, terminated
    hire_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Professional credentials
    license_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    license_expiry: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    certifications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array

    # Organizational assignment
    department_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    specialization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("specializations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Reporting structure
    supervisor_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Additional info
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    residential_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_login: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    password_changed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    account_locked_until: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
        foreign_keys="[user_roles.c.user_id, user_roles.c.role_id]",
        primaryjoin="User.id == user_roles.c.user_id",
        secondaryjoin="Role.id == user_roles.c.role_id",
    )

    branch_rel: Mapped["Branch"] = relationship(
        "Branch",
        back_populates="users",
        lazy="joined",
        foreign_keys=[branch_id]
    )

    department_rel: Mapped["Department"] = relationship(
        "Department",
        back_populates="users",
        lazy="joined",
        foreign_keys=[department_id]
    )

    specialization_rel: Mapped["Specialization"] = relationship(
        "Specialization",
        back_populates="users",
        lazy="joined",
        foreign_keys=[specialization_id]
    )

    supervisor: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[supervisor_id],
        lazy="joined",
        post_update=True
    )

    subordinates: Mapped[List["User"]] = relationship(
        "User",
        remote_side=[supervisor_id],
        foreign_keys=[supervisor_id],
        lazy="selectin",
        post_update=True
    )

    __table_args__ = (
        Index("idx_user_branch_active", "branch_id", "is_active"),
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_staff_id", "staff_id"),
        Index("idx_user_branch_department", "branch_id", "department_id"),
    )

    def __repr__(self) -> str:
        return f"<User {self.staff_id}: {self.full_name}>"

    @property
    def laboratory_name(self) -> Optional[str]:
        return self.branch_rel.laboratory_rel.name if self.branch_rel and self.branch_rel.laboratory_rel else None

    @property
    def branch_name(self) -> Optional[str]:
        return self.branch_rel.name if self.branch_rel else None

    @property
    def department_name(self) -> Optional[str]:
        return self.department_rel.name if self.department_rel else None

    @property
    def full_location(self) -> str:
        if self.branch_rel.laboratory_rel.is_multi_branch:
            return f"{self.laboratory_name} - {self.branch_name} - {self.department_name}"
        return f"{self.laboratory_name} - {self.department_name}"

    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)

    def works_at_laboratory(self, laboratory_id: int) -> bool:
        """Check if user works at specific laboratory (tenant check)."""
        return self.branch_rel.laboratory_id == laboratory_id