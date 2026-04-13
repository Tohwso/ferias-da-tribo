"""
Model SQLAlchemy: Person (Pessoa).

Membro de um time, com e-mail único.
Ref: domain_model.md §3.2 | BR-001, BR-009, BR-011
"""

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("team.id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # Relacionamentos
    team: Mapped["Team"] = relationship("Team", back_populates="persons")  # noqa: F821
    vacations: Mapped[list["Vacation"]] = relationship(  # noqa: F821
        "Vacation",
        back_populates="person",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Person(id={self.id}, name='{self.name}', email='{self.email}')>"
