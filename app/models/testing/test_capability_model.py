from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Integer, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.testing.test_catalog_model import Test
    from app.models.core.branch_model import Branch


class BranchTestCapability(Base):
    """
    Defines which tests each branch CAN PERFORM (not just order).
    All branches can order any test, but only some can perform them.
    """

    __tablename__ = "branch_test_capabilities"

    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    branch_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    test_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Capability
    can_perform: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Processing Details (overrides test defaults)
    turnaround_time_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    daily_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Audit
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    # Relationships
    branch_rel: Mapped["Branch"] = relationship("Branch", back_populates="test_capabilities", lazy="joined")
    test_rel: Mapped["Test"] = relationship("Test", back_populates="branch_capabilities", lazy="joined")

    # Constraints & Indexes
    __table_args__ = (
        Index("idx_branch_test", "branch_id", "test_id", unique=True),
        Index("idx_branch_capable", "branch_id", "can_perform", "is_active"),
        Index("idx_test_capable", "test_id", "can_perform", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<BranchTestCapability branch={self.branch_id} test={self.test_id} can={self.can_perform}>"
