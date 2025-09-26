# 智能试卷系统 MVP

> 基于 React + FastAPI 的现代化考试管理系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Ant Design Pro](https://img.shields.io/badge/Ant%20Design%20Pro-5.x-red.svg)](https://pro.ant.design/)

## ✨ 功能特性

### 🎯 核心功能
- **题库管理** - 支持多种题型的创建、编辑、分类和搜索
- **试卷构建** - 智能组卷，支持按知识点和难度分配
- **扫描上传** - OCR/OMR 答题卡识别和处理
- **成绩报告** - 详细的学生成绩分析和统计
- **拆题入库** - AI 辅助的试题解析和入库审核
- **用户权限** - 多角色权限管理（管理员/教师/学生）

### 🎨 技术特色
- **现代化UI** - 基于 Ant Design Pro 的企业级界面
- **响应式设计** - 适配桌面和移动设备
- **实时反馈** - 统一的错误处理和消息提示
- **表单验证** - 完整的前端验证和异步检查
- **数据可视化** - 丰富的图表和统计分析

## 🚀 快速开始

### 环境要求
- Node.js 16+
- Python 3.8+
- Git

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/SzSimonSun/smart-exam-mvp.git
cd smart-exam-mvp
```

2. **启动后端**
```bash
cd backend
# 安装依赖
pip install -r requirements.txt

# 初始化数据库和测试数据
python init_sqlite_enhanced.py

# 启动服务
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

3. **启动前端**
```bash
cd frontend_vite
# 安装依赖
npm install

# 配置环境变量
cp .env.example .env

# 启动开发服务器
npm run dev
```

4. **访问应用**
- 前端地址: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 测试账号
```
教师账号: teacher@example.com / password
学生账号: student@example.com / password
管理员: admin@example.com / password
```

## 📁 项目结构

```
smart-exam-mvp/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # 主应用和API路由
│   │   ├── config.py       # 配置文件
│   │   └── database.py     # 数据库连接
│   ├── init_sqlite_enhanced.py  # 数据库初始化
│   └── requirements.txt    # Python 依赖
├── frontend_vite/          # React 前端
│   ├── src/
│   │   ├── components/     # 共用组件
│   │   ├── hooks/          # React Hooks
│   │   ├── pages/          # 页面组件
│   │   ├── utils/          # 工具函数
│   │   └── App.jsx         # 主应用
│   ├── package.json        # 前端依赖
│   └── vite.config.js      # Vite 配置
├── test_data/              # 测试数据
└── docs/                   # 文档
```

## 🏗️ 技术架构

### 前端技术栈
- **React 18** - 现代化的用户界面框架
- **Vite** - 极速的构建工具
- **Ant Design Pro** - 企业级 UI 组件库
- **React Router** - 单页应用路由
- **Axios** - HTTP 客户端和错误处理
- **React Hooks** - 状态管理和逻辑复用

### 后端技术栈
- **FastAPI** - 高性能 Python Web 框架
- **SQLAlchemy** - Python SQL 工具包
- **SQLite** - 轻量级关系数据库
- **JWT** - JSON Web Token 认证
- **Uvicorn** - ASGI 服务器

### 核心特性
- **组件化架构** - 可复用的 React 组件和 Hooks
- **统一状态管理** - 基于 Context API 的认证状态
- **API 标准化** - RESTful API 设计和 OpenAPI 文档
- **错误处理** - 统一的前后端错误处理机制
- **开发体验** - 热重载、类型检查、调试工具

## 📚 功能模块

### 1. 认证系统
- JWT Token 认证
- 角色权限管理
- 登录状态持久化
- 自动刷新和登出

### 2. 题库管理
- 多题型支持（单选、多选、填空、主观题）
- 知识点分类管理
- 难度等级设置
- 批量操作和搜索

### 3. 试卷系统
- 智能组卷算法
- 试卷模板管理
- PDF 导出功能
- 试卷复制和修改

### 4. 扫描识别
- 答题卡上传
- OCR/OMR 处理
- 进度监控
- 结果验证

### 5. 成绩管理
- 自动批改
- 成绩统计分析
- 错题分析
- 报告生成

### 6. 拆题入库
- AI 辅助拆题
- 人工审核流程
- 批量处理
- 质量控制

## 🔧 开发指南

### API 接口

详细的 API 文档可在后端启动后访问：http://localhost:8000/docs

主要接口包括：
- `POST /api/auth/login` - 用户登录
- `GET /api/users/me` - 获取当前用户信息
- `GET /api/questions` - 获取题目列表
- `POST /api/questions` - 创建新题目
- `GET /api/papers` - 获取试卷列表
- `POST /api/papers` - 创建新试卷

### 回调接口
系统支持外部服务回调：
- `POST /api/callbacks/upload-progress` - 文件处理进度
- `POST /api/callbacks/ingest-result` - 拆题结果
- `POST /api/callbacks/grading-result` - 批改结果

### 数据库Schema
数据库表结构包括：
- `users` - 用户信息
- `questions` - 题目数据
- `papers` - 试卷信息
- `knowledge_points` - 知识点
- `answer_sheets` - 答题卡
- `upload_sessions` - 上传会话
- `ingest_sessions` - 拆题会话

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 License

本项目基于 MIT License - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Ant Design Pro](https://pro.ant.design/) - 优秀的企业级 UI 解决方案
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [React](https://reactjs.org/) - 灵活的前端框架
- [Vite](https://vitejs.dev/) - 极速的构建工具

---

**开发团队:** AI Assistant  
**项目状态:** MVP 阶段  
**最后更新:** 2024年9月