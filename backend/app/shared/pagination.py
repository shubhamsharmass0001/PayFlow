from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number starting from 1")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams):
        total_pages = (total + params.page_size - 1) // params.page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )


def paginate_query(query, params: PaginationParams):
    """Executes total count and window slicing on a SQLAlchemy query."""
    total = query.order_by(None).count()
    items = query.offset(params.offset).limit(params.limit).all()
    return items, total

