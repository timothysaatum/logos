from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.core.branch_model import Branch
    from app.models.staff.user_model import User


class Department(Base):
    """Lab departments within branches (e.g., Hematology, Microbiology)."""

    __tablename__ = "departments"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Identification
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Classification
    department_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: clinical_chemistry, hematology, microbiology, immunology,
    #        molecular_biology, histopathology, sample_collection, quality_control, administration

    # Department Head (nullable - can be set later)
    head_user_id: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Capacity
    staff_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    daily_test_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    # Relationships
    branch_rel: Mapped["Branch"] = relationship(
        "Branch",
        back_populates="departments",
        lazy="joined"
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        foreign_keys="User.department_id",
        back_populates="department_rel",
        lazy="noload"
    )

    head_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[head_user_id],
        lazy="joined",
        post_update=True
    )

    # Constraints & Indexes
    __table_args__ = (
        Index("idx_department_branch_code", "branch_id", "code", unique=True),
        Index("idx_department_type_active", "department_type", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} code='{self.code}'>"


class Specialization(Base):
    """Staff specializations/job roles (global, not per laboratory)."""

    __tablename__ = "specializations"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Identification
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    # Classification
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Categories: scientist, technician, phlebotomist, admin, management, it_support

    # Requirements
    requires_license: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    minimum_education: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Permissions/Capabilities
    can_approve_results: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_perform_tests: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_collect_samples: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="specialization_rel",
        lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<Specialization id={self.id} code='{self.code}'>"
