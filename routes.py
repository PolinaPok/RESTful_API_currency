from fastapi import APIRouter, HTTPException
from datetime import datetime
import requests
import re
from xml.etree import ElementTree as eT
from repository import CurrencyRepository
from models import Currencies
from xml.etree import ElementTree as ET

currency_router = APIRouter(prefix="/currencies", tags=["Currencies"])


@currency_router.post("/currencies")
async def load_currencies(date: str):
    """Метод загрузки в БД курсов валют за указанную дату.

    Укажите дату в формате YYYY-MM-DD.

    Если на указанную дату дынные присутствуют в БД, то запись не произойдет"""

    # Проверка, что дата подходит по формату
    try:
        date_object = datetime.strptime(date, '%Y-%m-%d')

        if date_object > datetime.now():
            raise HTTPException(
                status_code=400, detail="Указанная дата еще не наступила")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Некорректный формат даты. Дата должна иметь вид YYYY-MM-DD")

    try:
        # Проверка, существуют ли записи для этой даты
        check_saved = await CurrencyRepository.check_currency(date)

        if check_saved:
            raise HTTPException(
                status_code=400, detail="Данные за указанную дату уже существуют")
        else:
            response = requests.get(f'https://www.cbr.ru/scripts/XML_daily.asp', params={
                                    'date_req': date_object.strftime('%d/%m/%Y')})

            if response.status_code != 200:
                HTTPException(status_code=502,
                              detail="Ошибка при получении данных от ЦБ РФ")

            root = ET.fromstring(response.content)
            for valute in root.findall('Valute'):
                date = date
                charcode = valute.find('CharCode').text
                nominal = float(valute.find('Nominal').text)
                name = valute.find('Name').text
                value = float(valute.find('Value').text.replace(',', '.'))
                rate = round(value / nominal, 4)

                currency = Currencies(
                    date=date, charcode=charcode, nominal=nominal, name=name, value=value, rate=rate)

                await CurrencyRepository.add_currency(currency)

            return 'Currency rates saved successfully'
    except ValueError:
        raise HTTPException(
            status_code=500, detail="Внутренняя ошибка сервера")


@currency_router.get("/unique-currency-codes")
async def unique_currency_codes():
    """Метод получения списка уникальных кодов валют в БД"""
    result = await CurrencyRepository.get_currency_codes()
    return result


@currency_router.get("/all-data")
async def unique_currency_codes(page: int = 1, per_page: int = 10):
    """Метод постраничного получения всех данных из БД.

    Укажите номер страницы и количество элементов на странице, не превышающее 100."""
    max_per_page = 100
    # Проверка, что не превышено 100 элементов на странице
    if per_page > max_per_page:
        raise HTTPException(
            status_code=400, detail="Количество элементов на странице не должно превышать 100")
    else:
        # Получаем записи страницы
        query_result = await CurrencyRepository.get_page(page, per_page)
        # Получаем общее число строк в БД
        row_count = await CurrencyRepository.get_row_count()
        responce = {'page': page, per_page: per_page,
                    'total': row_count, 'items': [query_result]}
        return responce


@currency_router.delete("/delete-by-code")
async def delete_by_code(currency_code: str):
    """Метод удаления данных из БД по коду валют.

    Укажите код валюты латинскими бувами (пример, RON)."""
    currency_code = currency_code.upper()
    # Проверка соответствия формату
    cond = re.match(r"^[a-zA-Z]{3}$", currency_code)
    if not cond:
        raise HTTPException(
            status_code=400, detail="Неверный формат кода валюты")
    else:
        await CurrencyRepository.delete_by_charcode(currency_code)
        return f'All records for {currency_code} deleted successfully'
