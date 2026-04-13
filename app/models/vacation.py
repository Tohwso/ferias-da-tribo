"""
Model SQLAlchemy: Vacation (Evento de Férias).

Período de férias vinculado a uma pessoa, com cascata na exclusão.
Ref: domain_model.md §3.3 | BR-002, BR-003, BR-007, BR-009
"""

import datetime as _dt
from datetime import timezone

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> _dt.datetime:
    return _dt.datetime.now(timezone.utc)


class Vacation(Base):
    __tablename__ = "vacation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("person.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_date: Mapped[_dt.date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[_dt.date] = mapped_column(Date, nullable=False, index=True)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[_dt.datetime] = mapped_column(
        nullable=False, default=_utcnow
    )
    updated_at: Mapped[_dt.datetime] = mapped_column(
        nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # Relacionamento N:1
    person: Mapped["Person"] = relationship("Person", back_populates="vacations")  # noqa: F821

    __table_args__ = (
        CheckConstraint("start_date <= end_date", name="ck_vacation_dates"),
        CheckConstraint("days > 0", name="ck_vacation_days_positive"),
    )

    def __repr__(self) -> str:
        return (
            f"<Vacation(id={self.id}, person_id={self.person_id}, "
            f"{self.start_date} → {self.end_date}, {self.days}d)>"
        )
