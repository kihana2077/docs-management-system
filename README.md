# 文档管理系统

基于 **FastAPI + SQLAlchemy 2.0 + MySQL + Jinja2** 构建的轻量级文档（书籍）管理系统。支持文件上传、列表展示、在线下载和软删除，提供 Jinja2 渲染的 Web 界面和完整的 REST API。

---

## 功能特性

- 📁 **文件上传**：支持拖拽/点击上传，任意文件类型，自动以随机文件名落盘防冲突
- 📋 **文档列表**：卡片式展示，根据文件类型自动显示对应图标
- ⬇️ **文件下载**：一键下载，保留原始文件名
- 🗑️ **软删除**：删除只修改数据库标记，磁盘文件保留，数据可恢复
- 🌐 **Web 界面**：Bootstrap 5 响应式界面，无需额外前端框架
- 📖 **自动 API 文档**：FastAPI 自动生成 Swagger UI（`/docs`）

---

## 技术栈

| 层级 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| ORM | SQLAlchemy 2.0（异步） |
| 数据库 | MySQL（aiomysql 异步驱动） |
| 数据验证 | Pydantic v2 |
| 配置管理 | pydantic-settings（.env 读取） |
| 前端模板 | Jinja2 + Bootstrap 5 |
| 包管理器 | uv |

---

## 项目结构

```
docs-management-system/
│
├── backend/
│   ├── main.py          # FastAPI 入口，注册路由、挂载模板/静态资源
│   ├── config.py        # 读取 .env 的配置类
│   ├── database.py      # 异步引擎、Session 工厂、ORM 基类
│   ├── models.py        # 数据库模型（Docs 表）
│   ├── schemas.py       # Pydantic 请求/响应模型
│   ├── crud.py          # 数据库增删查业务逻辑
│   ├── routers/
│   │   └── books.py     # 文档相关 API 路由
│   └── uploads/         # 上传文件存储目录（自动创建）
│
├── templates/
│   ├── index.html       # 文档列表首页
│   └── upload.html      # 文件上传页
│
├── static/              # 自定义静态资源目录（CSS/JS/图片）
├── .env                 # 本地环境变量（不提交到仓库）
├── .env.example         # 环境变量模板（提交到仓库供参考）
└── pyproject.toml       # 项目依赖配置
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-username/docs-management-system.git
cd docs-management-system
```

### 2. 安装依赖

本项目使用 [uv](https://docs.astral.sh/uv/) 管理依赖：

```bash
# 安装 uv（如果尚未安装）
pip install uv

# 安装所有依赖
uv sync
```

### 3. 配置环境变量

复制模板并填入你的数据库信息：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
DB_HOST=your_mysql_host      # MySQL 服务器地址
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=fastapi_db           # 数据库名（需提前在 MySQL 中创建）
DB_CHARSET=utf8mb4

DB_ECHO=false                # 生产环境建议关闭 SQL 日志
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

UPLOAD_DIR=backend/uploads   # 文件存储目录
```

### 4. 创建数据库

在 MySQL 中执行：

```sql
CREATE DATABASE fastapi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> 数据库表会在**首次启动时自动创建**，无需手动执行建表 SQL。

### 5. 启动服务

```bash
uv run uvicorn backend.main:app --reload
```

启动成功后访问：

| 地址 | 说明 |
|------|------|
| http://127.0.0.1:8000 | 文档列表首页 |
| http://127.0.0.1:8000/upload | 上传文档页 |
| http://127.0.0.1:8000/docs | Swagger API 文档 |

---

## API 说明

所有接口均以 `/books` 为前缀。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/books/` | 获取所有未删除文档列表 |
| `POST` | `/books/upload` | 上传文档（multipart/form-data） |
| `GET` | `/books/{id}/download` | 下载指定文档 |
| `DELETE` | `/books/{id}` | 软删除指定文档 |

### 上传接口参数

`POST /books/upload` 接受 `multipart/form-data`：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 上传的文件 |
| `title` | string | ✅ | 文档标题（唯一） |
| `author` | string | ✅ | 作者 |
| `price` | float | ✅ | 价格（≥ 0） |
| `description` | string | ❌ | 描述（最多 255 字符） |

---

## 核心设计说明

### 文件与数据库的关联方式

上传文件时，系统做两件独立的事并通过数据库字段绑定：

1. **磁盘存储**：用 UUID 生成随机文件名落盘（如 `a3f8be...d2.pdf`），避免同名覆盖
2. **数据库记录**：写入一行元数据，其中：
   - `filename`：保留用户的原始文件名，下载时恢复此名称
   - `filepath`：服务器上的真实存储路径，下载时读取此路径

下载时根据 `id` 查到 `filepath` 读取文件，用 `filename` 设置下载名，两者分工明确。

### 软删除

删除操作不会从磁盘或数据库中真正移除数据，只将 `is_deleted` 字段置为 `True`。列表查询始终过滤该字段，被删除的文档对用户不可见，但数据保留，便于审计和恢复。

---

## 开发环境要求

- Python ≥ 3.13
- MySQL ≥ 5.7
- uv（包管理器）

---

## License

MIT
