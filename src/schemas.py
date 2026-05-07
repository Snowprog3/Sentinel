from pydantic import BaseModel, HttpUrl


class BookCreate(BaseModel):
    title: str
    price: str | None = None
    url: str


class BookOut(BaseModel):
    id: int
    title: str
    price: str | None
    url: str

    class Config:
        from_attrubutes = True
