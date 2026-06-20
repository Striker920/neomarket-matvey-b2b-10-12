from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from uuid import UUID


class SellerProductItem(BaseModel):
    id: UUID
    title: str
    slug: str
    status: str
    category_id: UUID
    deleted: bool
    category: Optional[dict] = None
    images: List[Any] = []
    characteristics: List[Any] = []
    skus_count: int = 0
    total_active_quantity: int = 0
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SellerProductsResponse(BaseModel):
    items: List[SellerProductItem] = []
    total_count: int = 0
    limit: int = 20
    offset: int = 0