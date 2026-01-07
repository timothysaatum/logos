from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.core.branch_model import Branch
    from app.models.patient.patient_model import Patient


class Laboratory(Base):
    """
    Top-level tenant - represents an independent lab organization.
    All data is isolated by laboratory_id for security.
    """

    __tablename__ = "laboratories"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Identification
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)

    # Lab Configuration
    lab_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: independent, hospital_lab, reference_lab, clinic_lab
    is_multi_branch: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Legal & Registration
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    license_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)

    # Contact
    primary_email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    primary_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Branding
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Subscription (SaaS Model)
    subscription_tier: Mapped[str] = mapped_column(String(50), nullable=False, default="basic")
    # Tiers: basic, professional, enterprise
    subscription_status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    # Status: active, suspended, cancelled, trial
    max_branches: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_users: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    max_monthly_tests: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    # Relationships
    branches: Mapped[List["Branch"]] = relationship(
        "Branch",
        back_populates="laboratory_rel",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    patients: Mapped[List["Patient"]] = relationship(
        "Patient",
        back_populates="laboratory_rel",
        lazy="noload"  # Don't load all patients by default
    )

    # Indexes
    __table_args__ = (
        Index("idx_lab_active_subscription", "is_active", "subscription_status"),
    )

    def __repr__(self) -> str:
        return f"<Laboratory id={self.id} name='{self.name}'>"
