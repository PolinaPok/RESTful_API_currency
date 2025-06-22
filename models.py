from pydantic import BaseModel, ConfigDict


class Currencies(BaseModel):
    date: str
    charcode: str
    nominal: float
    name: str
    value: float
    rate: float


class CurrenciesSaved(Currencies):
    id: int
    model_config = ConfigDict(from_attributes=True)