from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.laboratory.test_catalog_model import Test
    from app.models.laboratory.branch_model import Branch


class BranchTestAvailability(Base):
    """
    Defines which tests are available at which branches.
    If a test is not available at a branch, it gets referred to another branch.
    """
    
    __tablename__ = "branch_test_availability"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Which branch
    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Which test
    test_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Can this branch perform this test?
    can_perform: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # If not, where should samples be referred?
    refer_to_branch_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Operational details
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    daily_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Max tests per day
    
    # Additional TAT for referred tests (in hours)
    additional_tat_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    branch_rel: Mapped["Branch"] = relationship(
        "Branch",
        foreign_keys=[branch_id],
        lazy="joined"
    )
    
    test_rel: Mapped["Test"] = relationship(
        "Test",
        back_populates="branch_availability",
        lazy="joined"
    )
    
    refer_to_branch_rel: Mapped[Optional["Branch"]] = relationship(
        "Branch",
        foreign_keys=[refer_to_branch_id],
        lazy="joined"
    )
    
    # Unique constraint
    __table_args__ = (
        Index("idx_branch_test_unique", "branch_id", "test_id", unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<BranchTestAvailability branch={self.branch_id} test={self.test_id} can_perform={self.can_perform}>"