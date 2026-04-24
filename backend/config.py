from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 数据库连接的核心参数来自 .env，避免把账号密码写死在代码里。
    db_host: str = Field(..., alias="DB_HOST")
    db_port: int = 3306
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_name: str = Field(..., alias="DB_NAME")
    db_charset: str = "utf8mb4"

    db_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20

    upload_dir: str = "backend/uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def database_url(self) -> str:
        # 对密码做 URL 编码，避免特殊字符破坏连接串。
        password = quote_plus(self.db_password)
        return (
            f"mysql+aiomysql://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset={self.db_charset}"
        )


@lru_cache
def get_settings() -> Settings:
    # 配置对象只初始化一次，避免重复读取环境变量。
    return Settings()  # pyright: ignore[reportCallIssue]