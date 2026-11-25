from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(300))
    brand: Mapped[str | None] = mapped_column(String(100), index=True)
    gender: Mapped[str] = mapped_column(String(20), index=True)
    master_category: Mapped[str] = mapped_column(String(50), index=True)
    sub_category: Mapped[str] = mapped_column(String(50), index=True)
    article_type: Mapped[str] = mapped_column(String(50), index=True)
    colour: Mapped[str | None] = mapped_column(String(50))
    season: Mapped[str | None] = mapped_column(String(20))
    year: Mapped[int | None]
    usage: Mapped[str | None] = mapped_column(String(30))
    price: Mapped[int]