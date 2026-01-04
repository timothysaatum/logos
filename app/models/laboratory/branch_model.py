from sqlalchemy import String, Boolean, Integer, DateTime, Text, ForeignKey, Index, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.laboratory.department_model import Department
    from app.models.staff.user_model import User
    from app.models.laboratory.laboratory_model import Laboratory


class Branch(Base):

    """
    Branch/Location model - represents a physical lab location.
    For single-location labs, there's just one branch.
    For multi-branch labs, there can be multiple branches.
    """

    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to laboratory
    laboratory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("laboratories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Branch identification
    name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)  # e.g., "SynLab Accra Main"

    # Branch type
    branch_type: Mapped[str] = mapped_column(String(50), nullable=False)  # main_lab, satellite_lab, collection_point
    is_main_branch: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Location
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Ghana")
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # GPS coordinates
    latitude: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[Float]] = mapped_column(Float, nullable=True)

    # Contact
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Operational details
    operating_hours: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="Africa/Accra")

    # Capabilities
    has_testing_equipment: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_process_samples: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sample_collection_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Capacity
    daily_sample_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    storage_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Additional info
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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
        lazy="selectin"
    )

    # Unique constraints
    __table_args__ = (
        Index("idx_branch_lab_code", "laboratory_id", "code", unique=True),
        Index("idx_branch_lab_name", "laboratory_id", "name", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Branch id={self.id} name={self.name} lab_id={self.laboratory_id}>"

    @property
    def full_name(self) -> str:
        """Get full branch name including laboratory."""
        if self.display_name:
            return self.display_name
        return f"{self.laboratory_rel.name} - {self.name}"