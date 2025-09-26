# Smart Exam System - API 测试指南

## 🚀 已完成的核心 API

### 认证 & 用户管理

#### 1. 用户登录
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "teacher@example.com",
  "password": "password"
}

# PowerShell 测试：
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email": "teacher@example.com", "password": "password"}'

# 响应：
{
  "access_token": "token_for_2_648e6db0",
  "token_type": "bearer"
}
```

#### 2. 获取当前用户信息
```bash
GET /api/users/me
Authorization: Bearer {token}

# PowerShell 测试：
Invoke-RestMethod -Uri "http://localhost:8000/api/users/me" -Method GET -Headers @{"Authorization"="Bearer token_for_2_648e6db0"}

# 响应：
{
  "id": 2,
  "email": "teacher@example.com",
  "name": "Teacher Zhang",
  "role": "teacher"
}
```

### 知识点管理

#### 3. 获取知识点列表（树形结构）
```bash
GET /api/knowledge-points?subject={subject}&q={search}
Authorization: Bearer {token}

# PowerShell 测试：
Invoke-RestMethod -Uri "http://localhost:8000/api/knowledge-points" -Method GET -Headers @{"Authorization"="Bearer token_for_2_648e6db0"}

# 响应：
[
  {
    "id": 1,
    "subject": "Math",
    "module": "Algebra",
    "point": "Quadratic Equations",
    "code": "MATH_ALG_QUAD_ROOT",
    "level": 2
  },
  {
    "id": 3,
    "subject": "Math",
    "module": "Geometry", 
    "point": "Triangles",
    "code": "MATH_GEO_TRI_PYTH",
    "level": 2
  }
]
```

### 题库管理

#### 4. 创建题目
```bash
POST /api/questions
Authorization: Bearer {token}
Content-Type: application/json

{
  "stem": "什么是勾股定理？",
  "type": "single",
  "difficulty": 2,
  "options_json": {
    "A": "a^2 + b^2 = c^2",
    "B": "a + b = c",
    "C": "a * b = c", 
    "D": "a - b = c"
  },
  "answer_json": {
    "correct": "A"
  },
  "analysis": "勾股定理是直角三角形的基本定理",
  "knowledge_point_ids": [3]
}

# PowerShell 测试：
Invoke-RestMethod -Uri "http://localhost:8000/api/questions" -Method POST -Headers @{"Authorization"="Bearer token_for_2_648e6db0"; "Content-Type"="application/json"} -Body '{"stem": "什么是勾股定理？", "type": "single", "difficulty": 2, "options_json": {"A": "a^2 + b^2 = c^2", "B": "a + b = c"}, "answer_json": {"correct": "A"}, "knowledge_point_ids": [3]}'

# 响应：
{
  "id": 1,
  "stem": "什么是勾股定理？",
  "type": "single",
  "difficulty": 2,
  "status": "draft",
  "created_at": "2025-09-26T07:44:34.504237"
}
```

#### 5. 查询题目列表
```bash
GET /api/questions?kp={knowledge_point}&type={type}&difficulty={difficulty}&q={search}&page={page}&size={size}
Authorization: Bearer {token}

# PowerShell 测试：
Invoke-RestMethod -Uri "http://localhost:8000/api/questions" -Method GET -Headers @{"Authorization"="Bearer token_for_2_648e6db0"}

# 响应：
[
  {
    "id": 1,
    "stem": "什么是勾股定理？",
    "type": "single",
    "difficulty": 2,
    "status": "draft",
    "created_at": "2025-09-26T07:44:34.504237"
  }
]
```

#### 6. 发布题目
```bash
POST /api/questions/{question_id}/publish
Authorization: Bearer {token}

# PowerShell 测试：
Invoke-RestMethod -Uri "http://localhost:8000/api/questions/1/publish" -Method POST -Headers @{"Authorization"="Bearer token_for_2_648e6db0"}

# 响应：
{
  "message": "Question published successfully"
}
```

### 扫描上传（Mock）

#### 7. 上传答题卡
```bash
POST /api/answer-sheets/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

paper_id: 1
class_id: 1
file: [binary file]

# 响应：
{
  "status": "accepted",
  "paper_id": 1,
  "class_id": 1,
  "filename": "answer_sheet.jpg",
  "message": "File uploaded successfully, processing will begin shortly"
}
```

#### 8. 获取答题报告
```bash
GET /api/answer-sheets/{sheet_id}/report
Authorization: Bearer {token}

# PowerShell 测试：
Invoke-RestMethod -Uri "http://localhost:8000/api/answer-sheets/1/report" -Method GET -Headers @{"Authorization"="Bearer token_for_2_648e6db0"}

# 响应：
{
  "sheet_id": 1,
  "student_name": "学生示例",
  "paper_name": "示例试卷",
  "total_score": 95,
  "items": [
    {"question_id": 1, "score": 10, "is_correct": true},
    {"question_id": 2, "score": 8, "is_correct": false}
  ]
}
```

## 🔧 系统状态检查

### 健康检查
```bash
GET /health

# PowerShell 测试：
Invoke-RestMethod -Uri "http://localhost:8000/health"

# 响应：
{
  "status": "ok",
  "app": "Smart Exam System"
}
```

### API 文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 测试用户账户

| 角色 | 邮箱 | 密码 | 描述 |
|------|------|------|------|
| 管理员 | admin@example.com | password | 系统管理员 |
| 教师 | teacher@example.com | password | 张老师 |
| 学生 | student@example.com | password | 学生甲 |

## 🎯 下一步计划

### 已完成 ✅
- [x] 用户认证（登录、JWT）
- [x] 知识点管理 API
- [x] 题库管理 API（CRUD、发布）
- [x] 基础数据库连接和操作

### 待开发 📋
- [ ] 试卷构建 API (/api/papers)
- [ ] 试卷 PDF 导出功能
- [ ] 文件上传到 MinIO
- [ ] RabbitMQ 队列机制
- [ ] OCR/OMR Worker
- [ ] 自动判分系统
- [ ] 学情报表 API
- [ ] 试卷拆题入库功能

## 💡 技术说明

### 认证机制（当前简化版）
- 为了 MVP 快速开发，使用了简化的 token 机制
- 生产环境需要使用真正的 JWT 和密码哈希
- 当前密码验证为 mock 实现

### 数据库操作
- 使用原生 SQL 查询以确保性能和灵活性
- 支持复杂的联表查询和条件筛选
- 事务处理确保数据一致性

### API 设计特点
- RESTful 风格，符合标准
- 统一的错误处理
- 支持分页、筛选、搜索
- 完整的 CRUD 操作

---

**开发状态**: 🚀 核心 API 已完成，可以开始前端开发或继续后端功能扩展