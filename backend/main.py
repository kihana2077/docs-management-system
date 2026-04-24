from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from backend.config import get_settings
from backend.database import ASYNC_ENGINE, Base
from backend.routers.books import router as books_router
import backend.models  # noqa: F401

settings = get_settings()


async def create_tables() -> None:
	# 启动时同步元数据，保证首次运行时能自动建表。
	async with ASYNC_ENGINE.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
	# 服务启动时先确保上传目录和表结构存在。
	Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
	await create_tables()
	yield


app = FastAPI(title="Docs Management System", lifespan=lifespan)

app.include_router(books_router)


@app.get("/")
async def root():
	return {"message": "Docs management service is running."}
