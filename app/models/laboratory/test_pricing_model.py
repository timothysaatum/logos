from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Index, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING
from app.db.base import Base
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.laboratory.test_catalog_model import Test, TestPanel
    from app.models.laboratory.laboratory_model import Laboratory
    from app.models.laboratory.branch_model import Branch


class TestPrice(Base):
    """
    Test pricing - supports both standard pricing and branch-specific pricing.
    Standard price applies to all branches unless overridden.
    """
    
    __tablename__ = "test_prices"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Which laboratory (tenant isolation)
    laboratory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("laboratories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Which test (nullable if this is a panel price)
    test_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Which panel (nullable if this is a test price)
    panel_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("test_panels.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Pricing scope
    price_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  
    # standard (applies to all branches) or branch_specific
    
    # If branch-specific, which branch?
    branch_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Pricing
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GHS")  # GHS, USD, etc.
    
    # Discounts
    discount_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    
    # Final price after discount
    final_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Urgent/STAT pricing (higher price for faster results)
    urgent_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Price validity
    effective_from: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    effective_to: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    laboratory_rel: Mapped["Laboratory"] = relationship("Laboratory", lazy="joined")
    
    test_rel: Mapped[Optional["Test"]] = relationship(
        "Test",
        back_populates="prices",
        lazy="joined"
    )
    
    panel_rel: Mapped[Optional["TestPanel"]] = relationship(
        "TestPanel",
        back_populates="prices",
        lazy="joined"
    )
    
    branch_rel: Mapped[Optional["Branch"]] = relationship(
        "Branch",
        lazy="joined"
    )
    
    # Constraints
    __table_args__ = (
        # Either test_id or panel_id must be set, not both
        CheckConstraint(
            "(test_id IS NOT NULL AND panel_id IS NULL) OR (test_id IS NULL AND panel_id IS NOT NULL)",
            name="check_test_or_panel"
        ),
        # If price_type is branch_specific, branch_id must be set
        CheckConstraint(
            "(price_type = 'standard' AND branch_id IS NULL) OR (price_type = 'branch_specific' AND branch_id IS NOT NULL)",
            name="check_branch_price_consistency"
        ),
        # Unique pricing per scope
        Index("idx_test_standard_price", "laboratory_id", "test_id", "price_type", unique=True, postgresql_where="price_type = 'standard'"),
        Index("idx_test_branch_price", "laboratory_id", "test_id", "branch_id", unique=True, postgresql_where="price_type = 'branch_specific'"),
    )
    
    def __repr__(self) -> str:
        item_type = "Test" if self.test_id else "Panel"
        item_id = self.test_id or self.panel_id
        return f"<TestPrice {item_type}={item_id} {self.price_type} price={self.final_price} {self.currency}>"


class DiscountTier(Base):
    """
    Volume-based discount tiers.
    E.g., "Spend GHS 500 get 10% off", "Spend GHS 1000 get 15% off"
    """
    
    __tablename__ = "discount_tiers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Which laboratory
    laboratory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("laboratories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Discount tier details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Minimum amount to qualify (in base currency)
    minimum_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Discount to apply
    discount_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    
    # Alternative: fixed discount amount
    fixed_discount_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Tier conditions
    applies_to: Mapped[str] = mapped_column(String(20), nullable=False, default="all")  
    # all, single_visit, monthly_total, yearly_total
    
    # Validity
    effective_from: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    effective_to: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    laboratory_rel: Mapped["Laboratory"] = relationship("Laboratory", lazy="joined")
    
    def __repr__(self) -> str:
        return f"<DiscountTier {self.name}: {self.minimum_amount}+ = {self.discount_percentage}% off>"


class CorporateDiscount(Base):
    """
    Corporate/Organization-specific discounts.
    E.g., "Ghana Police Service gets 20% off all tests"
    """
    
    __tablename__ = "corporate_discounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Which laboratory
    laboratory_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("laboratories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Corporate client details
    organization_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    organization_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Discount details
    discount_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    
    # Applies to specific tests or all?
    applies_to_all_tests: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Contract details
    contract_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contract_start_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    contract_end_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    laboratory_rel: Mapped["Laboratory"] = relationship("Laboratory", lazy="joined")
    
    # Unique constraint
    __table_args__ = (
        Index("idx_lab_org_code", "laboratory_id", "organization_code", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<CorporateDiscount {self.organization_name}: {self.discount_percentage}% off>"