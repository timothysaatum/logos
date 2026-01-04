from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.staff.user_model import User
    from app.models.laboratory.branch_model import Branch


class Department(Base):
    """
    Department model - lab departments within a branch.
    Examples: Hematology, Microbiology, Sample Collection, Admin
    """

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to branch
    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Department info
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Department type
    department_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: clinical_chemistry, hematology, microbiology, immunology, molecular_biology,
    #        histopathology, sample_collection, quality_control, administration

    # Department head
    head_user_id: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Capacity & Resources
    staff_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    daily_test_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Test categories this department handles
    test_categories: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
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

    # Relationships
    branch_rel: Mapped["Branch"] = relationship(
        "Branch",
        back_populates="departments",
        lazy="joined"
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="department_rel",
        foreign_keys="User.department_id",
        lazy="selectin"
    )

    head: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[head_user_id],
        lazy="joined",
        post_update=True
    )

    # Unique per branch
    __table_args__ = (
        Index("idx_department_branch_code", "branch_id", "code", unique=True),
        Index("idx_department_branch_name", "branch_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name}>"


class Specialization(Base):
    """
    Specialization/Job Role model - staff specializations.
    Examples: Medical Lab Scientist, Lab Technician, Phlebotomist, Lab Manager
    """

    __tablename__ = "specializations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Specialization info
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Category
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    # Categories: scientist, technician, phlebotomist, admin, management, it_support

    # Qualification requirements
    requires_license: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    minimum_education: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Permissions & Capabilities
    can_approve_results: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_perform_tests: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_collect_samples: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
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

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="specialization_rel",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Specialization id={self.id} name={self.name}>"