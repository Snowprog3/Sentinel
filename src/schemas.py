from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class BookCreate(BaseModel):
    title: str
    price: str | None = None
    url: str
    raw_data: dict | None = None


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    price: str | None
    url: str
    raw_data: dict | None = None


class RawBookItem(BaseModel):
    """Raw data from spider"""

    title: str | None = None
    price: str | None = None
    url: str | None = None


class ParsedBook(BaseModel):
    """Data after cleaning and validation"""

    title: str
    price: float | None = None
    url: HttpUrl

    @field_validator("price", mode="before")
    @classmethod
    def clean_price(cls, v):
        if v is None:
            return None
        cleaned = str(v).replace("£", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            raise ValueError(f"Invalid price format - {v}")


class NormalizedBook(BaseModel):
    """Save data for database"""

    title: str
    price: float | None = None
    url: str
    raw_data: dict | None = None

    model_config = ConfigDict(from_attributes=True)
