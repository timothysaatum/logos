from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Index, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.testing.test_catalog_model import Test, TestPanel
    from app.models.core.laboratory_model import Laboratory
    from app.models.core.branch_model import Branch


class TestPrice(Base):
    """
    Test pricing - supports standard (lab-wide) and branch-specific pricing.
    Prices are denormalized/snapshotted in orders for historical accuracy.
    """

    __tablename__ = "test_prices"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Tenant Isolation
    laboratory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("laboratories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Foreign Keys - Either test_id OR panel_id (not both)
    test_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    panel_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("test_panels.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Pricing Scope
    price_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    # Types: standard (lab-wide), branch_specific

    # Branch-specific (null if standard)
    branch_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Pricing
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GHS")
    discount_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    final_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Urgent Pricing
    urgent_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Price Validity Period
    effective_from: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    effective_to: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    # Relationships
    laboratory_rel: Mapped["Laboratory"] = relationship("Laboratory", lazy="joined")
    test_rel: Mapped[Optional["Test"]] = relationship("Test", back_populates="prices", lazy="joined")
    panel_rel: Mapped[Optional["TestPanel"]] = relationship("TestPanel", back_populates="prices", lazy="joined")
    branch_rel: Mapped[Optional["Branch"]] = relationship("Branch", lazy="joined")

    # Constraints & Indexes
    __table_args__ = (
        # Must have either test_id or panel_id, not both
        CheckConstraint(
            "(test_id IS NOT NULL AND panel_id IS NULL) OR (test_id IS NULL AND panel_id IS NOT NULL)",
            name="check_test_or_panel"
        ),
        # If branch_specific, must have branch_id
        CheckConstraint(
            "(price_type = 'standard' AND branch_id IS NULL) OR (price_type = 'branch_specific' AND branch_id IS NOT NULL)",
            name="check_branch_price_consistency"
        ),
        # Unique pricing per scope
        Index("idx_test_standard_price", "laboratory_id", "test_id", "price_type", unique=True,
              postgresql_where="price_type = 'standard' AND test_id IS NOT NULL"),
        Index("idx_test_branch_price", "laboratory_id", "test_id", "branch_id", unique=True,
              postgresql_where="price_type = 'branch_specific' AND test_id IS NOT NULL"),
        Index("idx_panel_standard_price", "laboratory_id", "panel_id", "price_type", unique=True,
              postgresql_where="price_type = 'standard' AND panel_id IS NOT NULL"),
        Index("idx_panel_branch_price", "laboratory_id", "panel_id", "branch_id", unique=True,
              postgresql_where="price_type = 'branch_specific' AND panel_id IS NOT NULL"),
        # Query optimization indexes
        Index("idx_price_lab_active", "laboratory_id", "is_active"),
        Index("idx_price_validity", "effective_from", "effective_to"),
    )

    def __repr__(self) -> str:
        item_type = "Test" if self.test_id else "Panel"
        item_id = self.test_id or self.panel_id
        return f"<TestPrice {item_type}={item_id} type={self.price_type} price={self.final_price}>"


class DiscountTier(Base):
    """Volume-based discount tiers (e.g., spend GHS 500 get 10% off)."""

    __tablename__ = "discount_tiers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Tenant Isolation
    laboratory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("laboratories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Tier Details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Threshold & Discount
    minimum_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, index=True)
    discount_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    fixed_discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    # Application Scope
    applies_to: Mapped[str] = mapped_column(String(20), nullable=False, default="single_visit")
    # Types: single_visit, daily, monthly, yearly

    # Validity
    effective_from: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    effective_to: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    # Relationships
    laboratory_rel: Mapped["Laboratory"] = relationship("Laboratory", lazy="joined")

    __table_args__ = (
        Index("idx_discount_lab_active", "laboratory_id", "is_active"),
        Index("idx_discount_threshold", "minimum_amount"),
    )

    def __repr__(self) -> str:
        return f"<DiscountTier {self.name}: {self.minimum_amount}+ = {self.discount_percentage}%>"


class CorporateDiscount(Base):
    """Corporate/organizational discounts."""

    __tablename__ = "corporate_discounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Tenant Isolation
    laboratory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("laboratories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Organization Details
    organization_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    organization_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Discount
    discount_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    applies_to_all_tests: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Contract
    contract_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contract_start_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    contract_end_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    # Relationships
    laboratory_rel: Mapped["Laboratory"] = relationship("Laboratory", lazy="joined")

    __table_args__ = (
        Index("idx_corporate_lab_code", "laboratory_id", "organization_code", unique=True),
        Index("idx_corporate_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<CorporateDiscount {self.organization_name}: {self.discount_percentage}%>"
