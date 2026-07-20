from pydantic import BaseModel, Field, field_validator


class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float = Field(gt=0)  # ★ 가격이 0 이하(음수 포함)이면 거부

    @field_validator("category")
    @classmethod
    def lower_category(cls, v):
        # ★ 카테고리 텍스트 양쪽 공백 제거 및 소문자화 정규화 수행
        return v.strip().lower()