from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, DateTime, Float, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.core.laboratory_model import Laboratory
    from app.models.core.department_model import Department
    from app.models.staff.user_model import User
    from app.models.testing.test_capability_model import BranchTestCapability


class Branch(Base):
    """Physical lab locations where services are provided."""

    __tablename__ = "branches"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    laboratory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("laboratories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Identification
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # Branch Type & Role
    branch_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: main_lab, satellite_lab, collection_point, reference_center
    is_main_branch: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Location
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Ghana")
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # GPS Coordinates (for mapping/routing)
    latitude: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)

    # Contact
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Operational
    operating_hours: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="Africa/Accra")

    # Capabilities
    has_testing_equipment: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_process_samples: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sample_collection_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Capacity
    daily_sample_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    # Relationships
    laboratory_rel: Mapped["Laboratory"] = relationship(
        "Laboratory",
        back_populates="branches",
        lazy="joined"
    )

    departments: Mapped[List["Department"]] = relationship(
        "Department",
        back_populates="branch_rel",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="branch_rel",
        lazy="noload"
    )

    test_capabilities: Mapped[List["BranchTestCapability"]] = relationship(
        "BranchTestCapability",
        back_populates="branch_rel",
        lazy="noload"
    )

    # Constraints & Indexes
    __table_args__ = (
        Index("idx_branch_lab_code", "laboratory_id", "code", unique=True),
        Index("idx_branch_lab_active", "laboratory_id", "is_active"),
        Index("idx_branch_type_active", "branch_type", "is_active"),
        CheckConstraint(
            "(sample_collection_only = false) OR (sample_collection_only = true AND can_process_samples = false)",
            name="check_collection_point_logic"
        ),
    )

    def __repr__(self) -> str:
        return f"<Branch id={self.id} code='{self.code}' lab_id={self.laboratory_id}>"
