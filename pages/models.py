from dataclasses import dataclass


@dataclass
class ProductInfo:
    name: str
    price: float
    index: int


@dataclass(frozen=True)
class StoredProductInfo:
    name: str
    picture_url: str
    description: str
    price: float
