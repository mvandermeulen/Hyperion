from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Advertiser(Base):
    __tablename__ = "advert_advertisers"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    group_manager_id: Mapped[str] = mapped_column(String, nullable=False)

    adverts: Mapped[list["Advert"]] = relationship(
        "Advert", lazy="subquery", back_populates="advertiser"
    )


class Advert(Base):
    __tablename__ = "advert_adverts"

    id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    advertiser_id: Mapped[str] = mapped_column(ForeignKey("advert_advertisers.id"))
    advertiser: Mapped[Advertiser] = relationship(
        "Advertiser",
        lazy="joined",
        back_populates="adverts",
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tags: Mapped[str] = mapped_column(String, nullable=True)
