from pydantic import BaseModel, ConfigDict


class BookCreate(BaseModel):
    title: str
    price: str | None = None
    url: str
    raw_data: dict | None = None


class BookOut(BaseModel):
    model_config = ConfigDict(from_attrubutes=True)
    id: int
    title: str
    price: str | None
    url: str
    raw_data: dict | None = None

