from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from backend import crud
from backend.config import get_settings
from backend.database import ASYNC_ENGINE, Base, get_db
from backend.routers.books import router as books_router
import backend.models  # noqa: F401

settings = get_settings()

# 路径相对于项目根目录（backend/ 的上一级）
BASE_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


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

# 挂载静态资源目录，前端可通过 /static/... 路径引用
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# 把书籍相关的路由注册到主应用上，保持代码模块化和清晰
app.include_router(books_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
	# 从数据库拉取所有未删除文档，传给模板渲染首页列表。
	docs = await crud.get_docs(db)
	return templates.TemplateResponse(
		request=request, name="index.html", context={"docs": docs}
	)


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
	# 上传页只渲染静态表单，不需要查询数据库。
	return templates.TemplateResponse(
		request=request, name="upload.html"
	)
