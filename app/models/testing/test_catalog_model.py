from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.testing.test_capability_model import BranchTestCapability
    from app.models.testing.test_pricing_model import TestPrice


class TestCategory(Base):
    """Test categories (e.g., Hematology, Chemistry)."""

    __tablename__ = "test_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    tests: Mapped[List["Test"]] = relationship("Test", back_populates="category_rel", lazy="noload")

    def __repr__(self) -> str:
        return f"<TestCategory id={self.id} code='{self.code}'>"


class Test(Base):
    """
    Test catalog - defines all available tests.
    Tests are GLOBAL (not tenant-specific), but availability varies by branch.
    """

    __tablename__ = "tests"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Identification
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    short_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Test Details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clinical_significance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preparation_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Specimen Requirements
    specimen_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Types: blood_serum, blood_plasma, blood_whole, urine, stool, csf, sputum, swab, tissue
    specimen_volume: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    specimen_container: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    specimen_storage_temp: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    specimen_stability_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Processing Details
    turnaround_time_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=24)
    urgent_turnaround_time_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Result Information
    result_type: Mapped[str] = mapped_column(String(50), nullable=False, default="quantitative")
    # Types: quantitative, qualitative, semi_quantitative, text, image
    unit_of_measurement: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reference_range_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Test Complexity
    complexity_level: Mapped[str] = mapped_column(String(20), nullable=False, default="standard", index=True)
    # Levels: waived, standard, high_complexity, specialized

    # Equipment & Accreditation
    requires_specialized_equipment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_accreditation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Display & Popularity
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    # Relationships
    category_rel: Mapped["TestCategory"] = relationship("TestCategory", back_populates="tests", lazy="joined")

    branch_capabilities: Mapped[List["BranchTestCapability"]] = relationship(
        "BranchTestCapability",
        back_populates="test_rel",
        lazy="noload"
    )

    prices: Mapped[List["TestPrice"]] = relationship(
        "TestPrice",
        back_populates="test_rel",
        lazy="noload"
    )

    # Indexes
    __table_args__ = (
        Index("idx_test_category_active", "category_id", "is_active"),
        Index("idx_test_complexity_active", "complexity_level", "is_active"),
        Index("idx_test_specimen", "specimen_type"),
    )

    def __repr__(self) -> str:
        return f"<Test id={self.id} code='{self.code}'>"


class TestPanel(Base):
    """Test panels/packages - groups of tests sold together."""

    __tablename__ = "test_panels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Identification
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clinical_use: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Pricing
    is_discounted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Display
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    category_rel: Mapped["TestCategory"] = relationship("TestCategory", lazy="joined")

    panel_tests: Mapped[List["TestPanelItem"]] = relationship(
        "TestPanelItem",
        back_populates="panel_rel",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    prices: Mapped[List["TestPrice"]] = relationship(
        "TestPrice",
        back_populates="panel_rel",
        lazy="noload"
    )

    def __repr__(self) -> str:
        return f"<TestPanel id={self.id} code='{self.code}'>"


class TestPanelItem(Base):
    """Individual tests within a panel."""

    __tablename__ = "test_panel_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    panel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_panels.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    test_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    panel_rel: Mapped["TestPanel"] = relationship("TestPanel", back_populates="panel_tests")
    test_rel: Mapped["Test"] = relationship("Test", lazy="joined")

    __table_args__ = (
        Index("idx_panel_test", "panel_id", "test_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<TestPanelItem panel={self.panel_id} test={self.test_id}>"
