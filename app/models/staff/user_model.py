from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Boolean, DateTime, Index, Text, Integer, ForeignKey, Date, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.db import Base

if TYPE_CHECKING:
    from app.models.staff.rbac_model import Role
    from app.models.core.department_model import Department, Specialization
    from app.models.core.branch_model import Branch


class User(Base):
    """Lab staff members."""

    __tablename__ = "users"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Tenant Isolation - Critical for multi-tenant security
    # All queries MUST filter by laboratory_id
    laboratory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("laboratories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Foreign Keys - Organizational Structure
    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

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

    # Authentication
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    staff_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    telephone: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    date_of_birth: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Employment
    employee_type: Mapped[str] = mapped_column(String(50), nullable=False, default="full_time", index=True)
    # Types: full_time, part_time, contract, intern, consultant
    employment_status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    # Status: active, on_leave, suspended, terminated
    hire_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    termination_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Professional Credentials
    license_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    license_expiry: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)

    # Reporting Structure
    supervisor_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Additional Info
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    residential_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Security & Access Control
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Account Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_login: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    password_changed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    account_locked_until: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Audit Trail
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Soft Delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin"
    )

    branch_rel: Mapped["Branch"] = relationship(
        "Branch",
        back_populates="users",
        lazy="joined"
    )

    department_rel: Mapped["Department"] = relationship(
        "Department",
        foreign_keys=[department_id],
        back_populates="users",
        lazy="joined"
    )

    specialization_rel: Mapped["Specialization"] = relationship(
        "Specialization",
        back_populates="users",
        lazy="joined"
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
        lazy="noload",
        post_update=True
    )

    # Composite Indexes - Optimized for common queries
    __table_args__ = (
        # Tenant isolation index - CRITICAL
        Index("idx_user_lab_active", "laboratory_id", "is_active"),
        Index("idx_user_lab_branch", "laboratory_id", "branch_id"),

        # Authentication indexes
        Index("idx_user_email_active", "email", "is_active"),
        Index("idx_user_username_active", "username", "is_active"),
        Index("idx_user_staff_id_active", "staff_id", "is_active"),

        # Organizational indexes
        Index("idx_user_branch_dept", "branch_id", "department_id"),
        Index("idx_user_dept_spec", "department_id", "specialization_id"),

        # Employment indexes
        Index("idx_user_employment", "employee_type", "employment_status"),

        # Soft delete index
        Index("idx_user_deleted", "is_deleted", "deleted_at"),

        # Check constraints
        CheckConstraint(
            "(is_deleted = false AND deleted_at IS NULL) OR (is_deleted = true AND deleted_at IS NOT NULL)",
            name="check_user_soft_delete_consistency"
        ),
    )

    def __repr__(self) -> str:
        return f"<User {self.staff_id}: {self.first_name} {self.last_name}>"

    @property
    def full_name(self) -> str:
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    def has_role(self, role_name: str) -> bool:
        """Check if user has specific role."""
        return any(role.name == role_name for role in self.roles)
