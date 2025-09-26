
# Smart Exam System (V3.1) — MVP Starter

🎉 **最新更新**: 完整的登录功能和前后端集成已实现！

Generated on 2025-09-26T06:09:20

## ✨ 最新功能

### 🔐 完整的登录系统
- ✅ 用户认证和JWT Token管理
- ✅ 受保护的路由和页面访问控制
- ✅ 自动登录状态检查和重定向
- ✅ 安全的退出登录功能

### 📊 实时数据展示
- ✅ 题库页面显示真实后端数据
- ✅ 知识点管理系统
- ✅ 题目CRUD操作API
- ✅ 完整的前后端数据交互

### 🎨 用户界面
- ✅ 响应式登录界面
- ✅ 现代化的题库管理页面
- ✅ 状态标签和操作按钮
- ✅ 加载状态和错误处理

## 🚀 快速体验

### 测试账号
- **邮箱**: `teacher@example.com`
- **密码**: `password`

### 在线演示
1. 启动服务 (见下方快速启动)
2. 访问: http://localhost:5173
3. 使用测试账号登录
4. 体验完整的题库管理功能

## What's inside
- `schema.sql` — PostgreSQL schema for MVP
- `openapi.yaml` — Minimal API contract for core flows
- `docker-compose.yml` — Dev stack (Postgres, Redis, RabbitMQ, MinIO, backend, frontend)
- `backend/` — FastAPI skeleton with health/upload/report
- `frontend/` — Placeholder README for Vite + React bootstrapping

## Quick Start

### 方式一：本地开发环境 (推荐)
```bash
# 1. 克隆项目
git clone <your-repo-url>
cd smart-exam-mvp

# 2. 启动后端服务
cd backend
pip3 install -r requirements.txt
python3 init_sqlite.py  # 初始化测试数据
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. 启动前端服务 (新终端)
cd frontend_vite
npm install
npm run dev

# 4. 访问应用
# 前端: http://localhost:5173
# 后端API文档: http://localhost:8000/docs
```

### 方式二：Docker环境
如果您有Docker环境，可以使用原始的Docker配置：
1. Install Docker & Docker Compose.
2. Clone/extract this package and run:
   ```bash
   docker-compose up -d
   ```
3. Initialize DB:
   ```bash
   docker exec -i smart_exam_pg psql -U exam -d examdb < /init/schema.sql
   ```
   (or run `psql` locally and execute `schema.sql`)

4. Backend API: http://localhost:8000/docs
5. Frontend dev server: http://localhost:5173

## 📊 功能状态

### ✅ 已实现功能
- **用户认证系统**: 登录/退出、JWT Token管理
- **知识点管理**: 查询和展示知识点树
- **题库管理**: 题目查询、创建、展示
- **API文档**: Swagger UI接口文档
- **响应式前端**: React + Ant Design组件

### 🚧 待实现功能
- **试卷构建**: 可视化出卷界面
- **扫描上传**: MinIO文件存储和OCR/OMR识别
- **自动判分**: 客观题评分算法
- **学情报表**: 成绩统计和分析
- **拆题入库**: 试卷OCR解析和人工审核

## Next Steps
- Implement MinIO upload in `/api/answer-sheets/upload` and queue OCR/OMR job.
- Flesh out API endpoints per `openapi.yaml`.
- Build teacher UI pages: Question Bank, Paper Builder, Upload & Progress, Reports, Ingest Review.
- Add unit/integration tests and edge-case dataset.

## Notes
- Default credentials for services:
  - Postgres: `exam/exam` DB `examdb`
  - MinIO: `minio/minio123` (console http://localhost:9001)
  - RabbitMQ console: http://localhost:15672 (guest/guest)
