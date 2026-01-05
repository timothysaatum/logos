from sqlalchemy import String, Boolean, Integer, DateTime, Text, Float, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, List, TYPE_CHECKING
from app.db.base import Base
from decimal import Decimal

if TYPE_CHECKING:
    from app.models.laboratory.test_pricing_model import TestPrice, BranchTestAvailability
    from app.models.laboratory.laboratory_model import Laboratory


class TestCategory(Base):
    """Test categories - e.g., Hematology, Chemistry, Microbiology."""
    
    __tablename__ = "test_categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Display order
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tests: Mapped[List["Test"]] = relationship("Test", back_populates="category_rel", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<TestCategory {self.code}: {self.name}>"


class Test(Base):
    """
    Test catalog - defines all available tests.
    Global across the system, but availability varies by branch.
    """
    
    __tablename__ = "tests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Test identification
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Category
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Test details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    clinical_significance: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preparation_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # e.g., "Fasting required"
    
    # Specimen requirements
    specimen_type: Mapped[str] = mapped_column(String(100), nullable=False)  # blood, urine, stool, etc.
    specimen_volume: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "5ml"
    specimen_container: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "EDTA tube"
    
    # Processing details
    turnaround_time_hours: Mapped[int] = mapped_column(Integer, nullable=False, default=24)  # Standard TAT
    urgent_turnaround_time_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Urgent TAT
    
    # Reference values
    reference_range_male: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    reference_range_female: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    reference_range_child: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    unit_of_measurement: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Test complexity
    complexity_level: Mapped[str] = mapped_column(String(20), nullable=False, default="standard")  
    # waived, standard, high_complexity, specialized
    
    # Equipment requirements
    requires_specialized_equipment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    equipment_required: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # JSON list
    
    # Accreditation
    requires_accreditation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    accreditation_body: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Featured tests
    
    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category_rel: Mapped["TestCategory"] = relationship("TestCategory", back_populates="tests", lazy="joined")
    
    # Test availability at different branches
    branch_availability: Mapped[List["BranchTestAvailability"]] = relationship(
        "BranchTestAvailability",
        back_populates="test_rel",
        lazy="selectin"
    )
    
    # Pricing (standard and branch-specific)
    prices: Mapped[List["TestPrice"]] = relationship(
        "TestPrice",
        back_populates="test_rel",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Test {self.code}: {self.name}>"


class TestPanel(Base):
    """
    Test panels/packages - group of tests sold together.
    E.g., "Full Blood Count", "Lipid Profile", "Liver Function Tests"
    """
    
    __tablename__ = "test_panels"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Panel identification
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Category
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("test_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Panel details
    clinical_use: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Pricing
    is_discounted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Cheaper than individual tests
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category_rel: Mapped["TestCategory"] = relationship("TestCategory", lazy="joined")
    
    panel_tests: Mapped[List["TestPanelItem"]] = relationship(
        "TestPanelItem",
        back_populates="panel_rel",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    # Panel pricing
    prices: Mapped[List["TestPrice"]] = relationship(
        "TestPrice",
        back_populates="panel_rel",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<TestPanel {self.code}: {self.name}>"


class TestPanelItem(Base):
    """Tests included in a panel."""
    
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
    
    # Display order
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Is this test optional in the panel?
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    panel_rel: Mapped["TestPanel"] = relationship("TestPanel", back_populates="panel_tests")
    test_rel: Mapped["Test"] = relationship("Test", lazy="joined")
    
    # Unique constraint
    __table_args__ = (
        Index("idx_panel_test_unique", "panel_id", "test_id", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<TestPanelItem panel_id={self.panel_id} test_id={self.test_id}>"