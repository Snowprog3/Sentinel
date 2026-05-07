from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    price: str | None = None
    url: str
    raw_data: dict | None = None


class BookOut(BaseModel):
    id: int
    title: str
    price: str | None
    url: str
    raw_data: dict | None = None

    class Config:
        from_attrubutes = True
