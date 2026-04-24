from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base

class Docs(Base):  #定义Docs模型类 继承自Base
    # 当前项目的核心表，用来记录上传文件的元数据和软删除状态。
    __tablename__ = "Docs"
    id: Mapped[int] = mapped_column(primary_key=True, comment="书ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, comment="书名")
    author: Mapped[str] = mapped_column(String(255), nullable=False, comment="作者")
    price: Mapped[float] = mapped_column(Float, nullable=False, comment="价格")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="描述")
    filename: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件名")
    filepath: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件路径")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否删除，false=未删除，true=已删除")