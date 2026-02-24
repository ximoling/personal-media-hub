# Personal Media Hub

一个简洁优雅的个人媒体管理系统，支持图片、视频、文档上传、管理和预览。

## 快速启动

### Windows
双击运行 `start.bat`

### Linux/Mac
```bash
bash start.sh
```

然后访问: http://localhost:8000

## 项目结构

```
personal-media-hub/
├── backend/                  # FastAPI后端
│   ├── app/
│   │   ├── api/             # API路由
│   │   │   ├── auth.py      # 用户认证
│   │   │   ├── files.py     # 文件管理
│   │   │   └── categories.py # 分类管理
│   │   ├── core/            # 核心配置
│   │   │   ├── config.py    # 配置
│   │   │   ├── database.py  # 数据库
│   │   │   └── security.py  # 安全工具
│   │   ├── models/          # 数据模型
│   │   ├── utils/           # 工具函数
│   │   └── main.py          # 应用入口
│   ├── data/                # 数据存储
│   │   ├── uploads/         # 上传文件
│   │   └── thumbs/          # 缩略图
│   └── requirements.txt     # Python依赖
│
├── frontend/                # Vue前端
│   └── index.html          # 单页应用
│
├── start.bat               # Windows启动脚本
├── start.sh                # Linux/Mac启动脚本
└── README.md               # 项目说明
```

## 功能特性

### 用户系统
- 用户注册/登录
- JWT Token认证
- 密码加密存储

### 文件上传
- 拖拽上传
- 点击选择上传
- 多文件并行上传
- 上传进度显示
- 文件类型验证
- 支持大文件（最大100MB）

### 文件管理
- 网格展示
- 缩略图预览
- 分类筛选（全部/图片/视频/文档）
- 搜索功能
- 文件预览
- 文件下载
- 文件删除
- 文件信息展示

### 支持的文件类型

**图片:** JPG, PNG, GIF, WEBP, BMP, SVG

**视频:** MP4, MOV, AVI, MKV, WebM

**文档:** PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, CSV, ZIP, RAR

## 技术栈

### 后端
- **FastAPI** - 现代Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **SQLite** - 轻量级数据库
- **Pillow** - 图像处理
- **JWT** - 用户认证

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - UI组件库
- **Axios** - HTTP客户端
- **原生CSS** - 样式设计

## 使用指南

### 1. 首次使用
1. 打开 http://localhost:8000
2. 点击"注册"创建账号
3. 使用新账号登录

### 2. 上传文件
1. 进入"上传文件"页面
2. 拖拽文件到上传区域，或点击选择文件
3. 等待上传完成
4. 留在上传页面继续上传或切换到文件管理

### 3. 管理文件
1. 进入"文件管理"页面
2. 查看所有上传的文件
3. 使用筛选按钮查看特定类型文件
4. 使用搜索框搜索文件名
5. 点击文件预览或下载
6. 点击删除按钮移除文件

## 配置说明

### 后端配置
编辑 `backend/app/core/config.py`:

```python
# 安全配置
SECRET_KEY = "your-secret-key"  # 生产环境请修改
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # Token有效期(24小时)

# 存储配置
UPLOAD_DIR = "./data/uploads"      # 上传文件目录
THUMB_DIR = "./data/thumbs"        # 缩略图目录
MAX_FILE_SIZE = 104857600          # 最大文件大小(100MB)

# 允许的文件类型
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp", ...]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/quicktime", ...]
ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword", ...]
```

### 前端配置
编辑 `frontend/index.html` 中的:

```javascript
// API配置
const API_BASE_URL = 'http://localhost:8000';  // 后端地址
```

## 开发指南

### 安装依赖

**后端:**
```bash
cd backend
pip install -r requirements.txt
```

### 运行开发服务器

**后端:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**前端:**
直接打开 `frontend/index.html` 或使用任意HTTP服务器

### API文档
启动后端后访问: http://localhost:8000/docs

## 数据库结构

### 用户表 (users)
- id: 主键
- username: 用户名(唯一)
- hashed_password: 密码哈希
- created_at: 创建时间

### 文件表 (files)
- id: 主键
- user_id: 用户ID(外键)
- filename: 存储文件名
- original_name: 原始文件名
- file_path: 文件路径
- thumb_path: 缩略图路径
- file_type: 文件类型(image/video/document)
- file_size: 文件大小(字节)
- mime_type: MIME类型
- width/height: 图片尺寸
- created_at: 创建时间

## 安全说明

1. **默认配置仅适合本地开发**
2. 生产环境请修改 `SECRET_KEY`
3. 建议在生产环境使用HTTPS
4. 定期备份 `data/database.db` 和上传的文件

## 更新日志

### v1.1.0 (2026-02-24)
- 添加视频上传支持
- 添加文档上传支持（PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX等）
- 添加文件类型筛选功能
- 添加文件搜索功能
- 支持多文件并行上传
- 上传后停留在上传页面
- 删除后保持当前筛选状态
- 提升文件大小限制到100MB

### v1.0.0 (2026-02-08)
- 初始版本发布
- 用户注册/登录
- 图片上传功能
- 缩略图自动生成
- 图片网格展示
- 图片预览和删除

## 许可证

MIT License - 仅供学习交流使用

---

**享受您的个人媒体库！**
