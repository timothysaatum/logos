from sqlalchemy import String, Boolean, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.laboratory.branch_model import Branch


class Laboratory(Base):
    """
    Laboratory tenant model - represents an independent lab organization.
    Can be a single location lab or a multi-branch lab network.
    """

    __tablename__ = "laboratories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)  # URL-friendly identifier

    # Lab type
    lab_type: Mapped[str] = mapped_column(String(50),
                                          nullable=False)  # independent, hospital_lab, reference_lab, clinic_lab

    # Multi-branch configuration
    is_multi_branch: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Registration & Legal
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    license_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Contact Information
    primary_email: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Branding
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    brand_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color

    # Additional info
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Subscription/Billing (for SaaS model)
    subscription_tier: Mapped[str] = mapped_column(String(50), nullable=False,
                                                   default="basic")  # basic, professional, enterprise
    subscription_status: Mapped[str] = mapped_column(String(50), nullable=False,
                                                     default="active")  # active, suspended, cancelled
    max_branches: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_users: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit fields
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
    branches: Mapped[List["Branch"]] = relationship(
        "Branch",
        back_populates="laboratory_rel",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Laboratory id={self.id} name={self.name}>"

    @property
    def main_branch(self) -> Optional["Branch"]:
        """Get the main/headquarters branch."""
        return next((b for b in self.branches if b.is_main_branch), None)

    @property
    def active_branches_count(self) -> int:
        """Count active branches."""
        return sum(1 for b in self.branches if b.is_active)