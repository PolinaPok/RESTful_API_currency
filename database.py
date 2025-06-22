from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Model(DeclarativeBase):
    pass


class CurrenciesORM(Model):
    __tablename__ = "currencies"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str]
    charcode: Mapped[str | None]
    nominal: Mapped[float | None]
    name: Mapped[str | None]
    value: Mapped[float | None]
    rate: Mapped[float | None]


engine = create_async_engine("sqlite+aiosqlite:///currencies.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
