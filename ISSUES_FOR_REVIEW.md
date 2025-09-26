# 智能考试系统 MVP - 问题检查清单

## 项目概述
- **GitHub仓库**: https://github.com/SzSimonSun/smart-exam-mvp.git
- **项目描述**: 智能考试系统MVP，支持试卷创建、答题卡上传、OCR/OMR识别、PDF导出等功能
- **技术栈**: React + FastAPI + SQLite + MinIO

## 已知问题

### 1. 答题卡上传表单验证失败 ❌
**问题描述**: 
- 在答题卡上传页面，提交表单时出现验证错误
- 错误信息: `query -> paper_id: Field required query -> class_id: Field required`

**复现步骤**:
1. 登录系统 (用户名: admin, 密码: admin123)
2. 访问答题卡上传页面 (`/upload-scan`)
3. 选择试卷和班级
4. 上传答题卡文件
5. 点击提交，出现表单验证失败

**技术细节**:
- 后端API (`/api/answer-sheets/upload`) 期望 `paper_id` 和 `class_id` 作为查询参数
- 前端当前实现将这些参数作为 FormData 发送
- 需要修改前端代码将参数作为URL查询参数发送

**相关文件**:
- `frontend_vite/src/hooks/useUpload.js` (第63-75行)
- `backend/app/main.py` (第319行 - upload_answer_sheet 端点)

## 已实现功能

### ✅ 后端回调落库功能
- OCR/OMR处理结果回调端点: `/internal/ocr-omr/callback`
- 自动更新答题卡状态和识别结果
- 完整的数据库集成

### ✅ PDF导出功能
- 真实PDF生成使用 reportlab
- 集成二维码用于答题卡识别
- MinIO存储集成 (可选)
- 导出端点: `/api/papers/{paper_id}/export`

### ✅ 前端API集成
- 移除所有mock数据
- 完整的API对接
- JWT认证集成
- 响应式UI组件

## 环境配置

### 启动服务
```bash
# 启动所有服务
./start.sh

# 停止所有服务  
./stop.sh
```

### 测试用户
- 用户名: `admin`
- 密码: `admin123`

### 数据库
- SQLite数据库: `test_exam.db`
- 包含测试数据：试卷、用户、班级等

## 需要检查的重点

1. **参数传递问题**: 
   - 检查 `useUpload.js` 中的API调用方式
   - 确认后端API参数期望格式

2. **API兼容性**:
   - 前端FormData vs 后端查询参数
   - Content-Type处理

3. **错误处理**:
   - 前端表单验证逻辑
   - 后端参数验证机制

4. **架构设计**:
   - 文件上传流程是否合理
   - API设计是否符合RESTful规范

## 测试脚本

项目包含测试脚本 `test_upload.sh`，可以直接测试文件上传功能：

```bash
./test_upload.sh
```

## 联系信息
如有问题，请在GitHub Issues中反馈或直接联系项目维护者。

---
**最后更新**: 2025-09-26
**版本**: v1.0-mvp