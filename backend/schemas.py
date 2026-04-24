from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocsBase(BaseModel):
    # 这里定义创建和返回都会复用的公共字段。
    title: str = Field(..., min_length=1, max_length=255, description="文档标题")
    author: str = Field(..., min_length=1, max_length=255, description="作者")
    price: float = Field(..., ge=0, description="价格")
    description: str | None = Field(default=None, max_length=255, description="描述")


class DocsCreate(DocsBase):
    pass


class DocsUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    price: float | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=255)


class DocsUploadForm(DocsBase):
    model_config = ConfigDict(extra="forbid")


class DocsOut(DocsBase):
    # from_attributes=True 允许直接从 SQLAlchemy 模型实例生成响应数据。
    id: int
    filename: str
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)


class DeleteResponse(BaseModel):
    message: str
    doc_id: int