# 智能试卷系统（V3.1 增强版）开发指南

## 🎯 项目概述

### MVP 目标
实现最短闭环：**出卷** → **打印/分发** → **扫描上传** → **自动判分（客观题）** → **学情基础报表** + **教师辅助式试卷反向拆题入库**

### 技术架构
- **前端**: React 18 + Vite + Ant Design + React Router
- **后端**: FastAPI + SQLAlchemy + Pydantic
- **数据库**: PostgreSQL 14+
- **缓存**: Redis 7
- **消息队列**: RabbitMQ 3
- **对象存储**: MinIO (S3 兼容)
- **容器化**: Docker + Docker Compose

## 🔧 开发环境搭建

### 快速启动
```bash
# 1. 克隆项目（如果还没有）
git clone <repo-url>
cd smart-exam-mvp

# 2. 启动所有服务
docker-compose up -d

# 3. 初始化数据库
Get-Content schema.sql | docker exec -i smart_exam_pg psql -U exam -d examdb

# 4. 访问服务
# 前端: http://localhost:5173
# 后端API: http://localhost:8000/docs
# MinIO控制台: http://localhost:9011 (minio/minio123)
# RabbitMQ管理界面: http://localhost:15672 (guest/guest)
```

### 端口配置（已避免冲突）
- **PostgreSQL**: 5433 (外部) → 5432 (容器内)
- **Redis**: 6380 (外部) → 6379 (容器内)
- **RabbitMQ**: 5672, 15672
- **MinIO**: 9010 (API), 9011 (控制台)
- **Backend**: 8000
- **Frontend**: 5173

### 环境变量
复制 `.env.example` 到 `.env` 并根据需要调整配置。

## 📊 数据库设计

### 核心表结构
1. **用户与权限**: `users`, `classes`, `class_students`
2. **知识点与题库**: `knowledge_points`, `questions`, `question_knowledge_map`
3. **试卷系统**: `papers`, `paper_questions`, `paper_versions`
4. **扫描与批阅**: `answer_sheets`, `answers`, `grading_logs`
5. **学情分析**: `student_stats`, `wrong_book`
6. **拆题入库**: `ingest_sessions`, `ingest_items`

### 索引优化
- 用户角色查询: `idx_users_role`, `uniq_users_email`
- 知识点层级: `idx_kp_subject_module`, `idx_kp_parent`
- 题目分类: `idx_questions_type_difficulty`, `idx_questions_status`
- 答案分析: `idx_answers_sheet_qid`, `idx_answers_qid_correct`
- 学情统计: `idx_student_stats_student_kp`

### 测试数据
系统已预置3个测试用户：
- `admin@example.com` - 系统管理员
- `teacher@example.com` - 教师
- `student@example.com` - 学生

密码均为: `password` (哈希后存储)

## 🔄 开发工作流

### 分支策略
- `main` - 生产分支（受保护）
- `develop` - 开发分支
- `feature/*` - 功能分支
- `hotfix/*` - 紧急修复

### 代码规范
- **Python**: PEP 8, Black 格式化, mypy 类型检查
- **JavaScript**: ESLint + Prettier, JSDoc 注释
- **提交信息**: `type(scope): description` 格式

### API 文档
- Swagger UI: http://localhost:8000/docs
- OpenAPI 规范: `/openapi.yaml`

## 🏗️ 系统模块

### 1. 用户认证模块
- JWT Token 认证
- 角色权限控制
- 登录/登出功能

### 2. 题库管理模块
- 知识点树形结构
- 题目CRUD操作
- 题目分类与标签

### 3. 试卷构建模块
- 可视化出卷界面
- PDF导出（带QR码）
- 多版本防作弊

### 4. 扫描识别模块
- MinIO文件上传
- OCR文字识别
- OMR选择题识别
- 异步任务队列

### 5. 自动判分模块
- 客观题自动评分
- 数据质量检查
- 异常情况处理

### 6. 学情报表模块
- 个人成绩报告
- 班级统计分析
- 知识点掌握度

### 7. 拆题入库模块
- 试卷OCR解析
- 题目智能分割
- 教师人工校对

## 🚀 开发任务清单

✅ **阶段1: 系统环境搭建**
- [x] Docker容器服务启动
- [x] 数据库初始化
- [x] 前端开发环境配置

🔄 **阶段2: 后端核心API开发**
- [ ] 用户认证模块
- [ ] 数据库连接和CRUD
- [ ] 知识点管理API
- [ ] 题库管理API

📋 **阶段3: 试卷生成模块**
- [ ] 试卷构建API
- [ ] PDF导出功能
- [ ] 前端题库管理页面
- [ ] 前端试卷构建页面

🔍 **阶段4: 扫描上传与识别**
- [ ] MinIO文件存储
- [ ] RabbitMQ队列机制
- [ ] OCR Worker开发
- [ ] OMR Worker开发
- [ ] 前端上传页面

⚡ **阶段5: 自动判分系统**
- [ ] 客观题判分逻辑
- [ ] 答案比对算法
- [ ] 数据质量检查

📊 **阶段6: 学情报表系统**
- [ ] 个人成绩报告API
- [ ] 班级统计功能
- [ ] 知识点统计
- [ ] 前端报表页面

🔄 **阶段7: 试卷拆题入库**
- [ ] 试卷OCR解析
- [ ] 题目分割识别
- [ ] 人工校对工作流
- [ ] 前端审核页面

🧪 **阶段8: 系统集成测试**
- [ ] 端到端流程测试
- [ ] 测试数据准备
- [ ] 性能优化
- [ ] 文档完善

## 🔍 调试与监控

### 容器日志查看
```bash
# 查看所有服务状态
docker-compose ps

# 查看特定服务日志
docker logs smart_exam_backend
docker logs smart_exam_frontend
docker logs smart_exam_pg

# 实时跟踪日志
docker logs -f smart_exam_backend
```

### 数据库操作
```bash
# 连接数据库
docker exec -it smart_exam_pg psql -U exam -d examdb

# 查看表结构
\d users
\d questions

# 查询数据
SELECT * FROM users;
SELECT COUNT(*) FROM knowledge_points;
```

### 服务健康检查
- Backend健康检查: `curl http://localhost:8000/health`
- Frontend访问: http://localhost:5173
- MinIO控制台: http://localhost:9011
- RabbitMQ管理: http://localhost:15672

## 🛠️ 故障排除

### 常见问题
1. **端口冲突**: 检查 `netstat -ano | findstr "端口号"`
2. **容器启动失败**: 查看 `docker logs 容器名`
3. **前端构建错误**: 检查 `package.json` 配置
4. **数据库连接失败**: 验证连接字符串和凭据

### 重新初始化
```bash
# 完全重置环境
docker-compose down -v  # 删除数据卷
docker-compose up -d
Get-Content schema.sql | docker exec -i smart_exam_pg psql -U exam -d examdb
```

## 📝 下一步

当前环境已经完成搭建，接下来按照任务清单开始后端核心API的开发。建议按模块逐步实现，每个模块完成后进行单元测试和集成测试。

---

**开发团队**: Smart Exam Development Team  
**文档版本**: v1.0  
**更新时间**: 2025-09-26