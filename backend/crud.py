from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend import models, schemas


async def get_docs(db: AsyncSession) -> list[models.Docs]:
	# 统一在数据层过滤已软删除的数据，避免路由层重复写条件。
	result = await db.execute(
		select(models.Docs)
		.where(models.Docs.is_deleted.is_(False))
		.order_by(models.Docs.create_time.desc())
	)
	return list(result.scalars().all())

async def get_doc_by_id(db: AsyncSession, doc_id: int) -> models.Docs | None:
    result = await db.execute(
        select(models.Docs)
        .where(models.Docs.id == doc_id, models.Docs.is_deleted.is_(False))
    )
    return result.scalars().first()

async def create_doc(
	db: AsyncSession,
	doc_in: schemas.DocsCreate,
	*,
	filename: str,
	filepath: str,
) -> models.Docs:
	# 这里只负责数据库记录，不处理具体文件保存逻辑。
	doc = models.Docs(
		title=doc_in.title,
		author=doc_in.author,
		price=doc_in.price,
		description=doc_in.description,
		filename=filename,
		filepath=filepath,
	)
	db.add(doc)
	await db.commit()
	await db.refresh(doc)
	return doc


async def soft_delete_doc(db: AsyncSession, doc_id: int) -> models.Docs | None:
	# 软删除只修改标记位，不直接删除数据库记录。
	doc = await db.get(models.Docs, doc_id)
	if doc is None or doc.is_deleted:
		return None

	doc.is_deleted = True
	await db.commit()
	await db.refresh(doc)
	return doc
