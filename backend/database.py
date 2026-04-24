from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from backend.config import get_settings

settings = get_settings()

# 异步引擎负责和 MySQL 建立连接池。
ASYNC_ENGINE = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
)

AsyncSessionLocal = async_sessionmaker(
    bind=ASYNC_ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    # 所有模型共用创建时间和更新时间，减少重复字段定义。
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="创建时间",
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

#提供数据库会话的依赖注入函数，供 FastAPI 路由使用
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
