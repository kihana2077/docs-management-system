from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend import crud, schemas
from backend.config import get_settings
from backend.database import get_db

router = APIRouter(prefix="/books", tags=["books"])
settings = get_settings()


def _build_storage_path(filename: str) -> tuple[Path, str]:
	# 用随机文件名落盘，避免用户上传同名文件时互相覆盖。
	upload_dir = Path(settings.upload_dir)
	upload_dir.mkdir(parents=True, exist_ok=True)

	suffix = Path(filename).suffix
	stored_name = f"{uuid4().hex}{suffix}"
	file_path = upload_dir / stored_name
	return file_path, stored_name


@router.get("/", response_model=list[schemas.DocsOut])
async def list_docs(db: AsyncSession = Depends(get_db)):
	return await crud.get_docs(db)


@router.post("/upload", response_model=schemas.DocsOut, status_code=status.HTTP_201_CREATED)
async def upload_doc(
	title: str = Form(...),
	author: str = Form(...),
	price: float = Form(...),
	description: str | None = Form(None),
	file: UploadFile = File(...),
	db: AsyncSession = Depends(get_db),
):
	# 文件内容走 multipart/form-data，普通字段用 Form 接收。
	if not file.filename:
		raise HTTPException(status_code=400, detail="文件名不能为空")

	doc_in = schemas.DocsCreate(
		title=title,
		author=author,
		price=price,
		description=description,
	)

	file_path, stored_name = _build_storage_path(file.filename)
	# 先把文件保存到磁盘，再写数据库记录，避免数据库里出现无效路径。
	content = await file.read()
	file_path.write_bytes(content)

	try:
		return await crud.create_doc(
			db,
			doc_in,
			filename=file.filename,
			filepath=str(file_path).replace("\\", "/"),
		)
	except Exception:
		if file_path.exists():
			file_path.unlink()
		raise
	finally:
		await file.close()


@router.delete("/{doc_id}", response_model=schemas.DeleteResponse)
async def delete_doc(doc_id: int, db: AsyncSession = Depends(get_db)):
	doc = await crud.soft_delete_doc(db, doc_id)
	if doc is None:
		raise HTTPException(status_code=404, detail="文档不存在或已删除")
	return schemas.DeleteResponse(message="文档已删除", doc_id=doc.id)
