# Copyright (C) 2024 Aleksei Rogov <alekzzzr@gmail.com>. All rights reserved.

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ThermoModel(Base):
    __tablename__ = "thermo"
    id: Mapped[int] = mapped_column(primary_key=True)
    key_id: Mapped[int]
    sid: Mapped[str]
    mac: Mapped[str]
    temp: Mapped[float]
    pres: Mapped[float]
    hum: Mapped[float]
    adc: Mapped[float]
    timestamp: Mapped[int]


class KeyModel(Base):
    __tablename__ = "keys"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    key: Mapped[str]
    perm_delete_key: Mapped[bool]
    perm_delete_thermo: Mapped[bool]
    perm_read_key: Mapped[bool]
    perm_read_thermo: Mapped[bool]
    perm_add_key: Mapped[bool]
    perm_add_thermo: Mapped[bool]
    created: Mapped[int]
    enabled: Mapped[bool]
