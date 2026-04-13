"""
Model SQLAlchemy: Team (Time).

Representa um agrupamento organizacional.
Ref: domain_model.md §3.1 | BR-008, BR-010
"""

from datetime import datetime, timezone

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Team(Base):
    __tablename__ = "team"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # Relacionamento 1:N — Team possui muitas Persons
    persons: Mapped[list["Person"]] = relationship(  # noqa: F821
        "Person", back_populates="team"
    )

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}')>"
