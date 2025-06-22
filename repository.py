from database import CurrenciesORM, new_session
from models import Currencies, CurrenciesSaved
from sqlalchemy import select, func, delete


class CurrencyRepository:
    @classmethod
    async def add_currency(cls, currency: Currencies) -> int:
        async with new_session() as session:
            data = currency.model_dump()
            new_row = CurrenciesORM(**data)
            session.add(new_row)
            await session.flush()
            await session.commit()
            return new_row.id

    @classmethod
    async def get_currency(cls) -> list[Currencies]:
        async with new_session() as session:
            query = select(CurrenciesORM)  # .filter_by(date = user_date)
            result = await session.execute(query)
            currencies_models = result.scalars().all()
            currencies = [Currencies.model_validate(currency_model) for currency_model in currencies_models]
            return currencies_models

    @classmethod
    async def check_currency(cls, user_date: str) -> bool:
        async with new_session() as session:
            query = select(CurrenciesORM).filter_by(date=user_date).limit(1)
            result = await session.execute(query)
            return bool(result.first())

    @classmethod
    async def get_currency_codes(cls) -> list:
        async with new_session() as session:
            query = select(CurrenciesORM.charcode.distinct())
            result = await session.execute(query)
            uniques_charcodes = result.all()
            uniques_charcodes_list = [charcode for (charcode,) in uniques_charcodes]
            return uniques_charcodes_list

    @classmethod
    async def get_page(cls, page: int, per_page: int) -> list[CurrenciesSaved]:
        async with new_session() as session:
            offset = (page - 1) * per_page
            limit = per_page

            query = (
                select(CurrenciesORM)
                .offset(offset)
                .limit(limit)
                .order_by(CurrenciesORM.id)
            )

            result = await session.execute(query)
            currencies_models = result.scalars().all()
            currencies_list = [CurrenciesSaved.model_validate(currency_model) for currency_model in currencies_models]
            a = type(currencies_list)
            return currencies_list

    @classmethod
    async def get_row_count(cls) -> int:
        async with new_session() as session:
            query = select(func.count(CurrenciesORM.id))
            result = await session.execute(query)
            row_count = result.scalar_one()
            return row_count

    @classmethod
    async def delete_by_charcode(cls, currency_code: str):
        async with new_session() as session:
            statement = delete(CurrenciesORM).where(CurrenciesORM.charcode == currency_code)
            await session.execute(statement)
            await session.commit()
            return
