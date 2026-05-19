from sqlalchemy import Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    price: Mapped[str | None] = mapped_column(String(32), nullable=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)
    raw_data_key: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None)

    __table_args__ = (
        Index("idx_title", "title"),
        Index("idx_price", "price"),
        Index("idx_raw_data-gin", "raw_data", postgresql_using="gin"),
    )
