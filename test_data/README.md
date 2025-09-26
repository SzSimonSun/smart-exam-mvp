# 测试数据导入指南

## 📊 测试数据概述

本目录包含智能试卷系统的完整测试数据：
- **用户数据**: 6个测试用户（1个管理员，2个教师，3个学生）
- **班级数据**: 3个班级，完整的师生关系
- **知识点**: 22个知识点，覆盖数学、语文、英语
- **题库**: 11道题目，包含各种题型
- **试卷**: 3套完整试卷，含题目映射
- **答题记录**: 模拟学生答题数据

## 🚀 快速导入

### 方式一：SQL导入 (推荐)

#### Docker环境
```bash
# 确保Docker容器运行
docker-compose up -d

# 导入测试数据
docker cp test_data/data.sql smart_exam_pg:/data.sql
docker exec -it smart_exam_pg psql -U exam -d examdb -f /data.sql
```

#### 本地PostgreSQL
```bash
# 如果使用本地PostgreSQL
psql -U exam -d examdb -f test_data/data.sql
```

#### SQLite（本地测试）
```bash
# 如果使用SQLite进行本地测试
cd backend
python3 init_sqlite_enhanced.py
```

### 方式二：CSV导入

#### 准备CSV文件
```bash
# 将CSV文件复制到容器
docker cp test_data/knowledge_points.csv smart_exam_pg:/var/lib/postgresql/knowledge_points.csv
docker cp test_data/questions_enhanced.csv smart_exam_pg:/var/lib/postgresql/questions.csv
```

#### 在容器中执行导入
```bash
# 进入PostgreSQL容器
docker exec -it smart_exam_pg psql -U exam -d examdb

# 在psql中执行以下命令：
```

```sql
-- 导入知识点
COPY knowledge_points(subject,module,point,subskill,code,level)
FROM '/var/lib/postgresql/knowledge_points.csv' 
DELIMITER ',' CSV HEADER;

-- 导入题目
COPY questions(stem,type,difficulty,options_json,answer_json,analysis,source_meta,created_by,status)
FROM '/var/lib/postgresql/questions.csv' 
DELIMITER ',' CSV HEADER;
```

## 🔧 验证导入结果

### 检查数据完整性
```sql
-- 检查用户数据
SELECT COUNT(*), role FROM users GROUP BY role;

-- 检查知识点
SELECT COUNT(*), subject FROM knowledge_points GROUP BY subject;

-- 检查题目
SELECT COUNT(*), type FROM questions GROUP BY type;

-- 检查试卷
SELECT p.name, COUNT(pq.question_id) as question_count 
FROM papers p 
LEFT JOIN paper_questions pq ON p.id = pq.paper_id 
GROUP BY p.id, p.name;
```

### 测试登录账号
```
管理员: admin@example.com / password
教师1: teacher@example.com / password  
教师2: teacher2@example.com / password
学生1: student@example.com / password
学生2: student2@example.com / password
学生3: student3@example.com / password
```

## 🎯 快速联调建议

### 1. 启动完整环境
```bash
# 启动基础服务
docker-compose up -d

# 如果需要workers（OCR/OMR处理）
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# 导入测试数据
docker cp test_data/data.sql smart_exam_pg:/data.sql
docker exec -it smart_exam_pg psql -U exam -d examdb -f /data.sql
```

### 2. 启动前端
```bash
cd frontend_vite
npm install
npm run dev
```

### 3. 功能验证清单

#### 基础功能验证
- [ ] 用户登录：访问 http://localhost:5173，使用测试账号登录
- [ ] 题库查看：在题库页面确认可以看到11道测试题目
- [ ] 知识点管理：API调用确认22个知识点数据
- [ ] 试卷管理：确认3套试卷数据可见

#### API接口验证
```bash
# 登录获取token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "teacher@example.com", "password": "password"}'

# 查询知识点
curl -X GET "http://localhost:8000/api/knowledge-points" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查询题目
curl -X GET "http://localhost:8000/api/questions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 文件上传测试
```bash
# 测试答题卡上传（返回mock数据）
curl -X POST "http://localhost:8000/api/answer-sheets/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_image.jpg" \
  -F "paper_id=1" \
  -F "class_id=1"
```

#### Worker测试（如果启用）
```bash
# 检查worker服务状态
docker logs smart_exam_omr_worker
docker logs smart_exam_ocr_worker

# 模拟推送任务到队列
# 查看workers/test_workers.py了解测试方法
```

## 📁 文件说明

- `data.sql`: 完整的SQL测试数据，包含所有表的数据
- `knowledge_points.csv`: 知识点CSV格式数据
- `questions.csv`: 基础题目CSV数据  
- `questions_enhanced.csv`: 增强版题目CSV数据（推荐）
- `README.md`: 本说明文件

## ⚠️ 注意事项

1. **密码**: 所有测试用户密码都是 `password`（已进行bcrypt加密）
2. **数据清理**: 如需重新导入，可先清空相关表数据
3. **字符编码**: CSV文件使用UTF-8编码
4. **Docker版本**: 确保使用兼容的Docker和Docker Compose版本
5. **端口冲突**: 检查5432、6379等端口是否被占用

## 🚨 故障排除

### 导入失败
```bash
# 检查容器状态
docker-compose ps

# 查看PostgreSQL日志
docker logs smart_exam_pg

# 检查数据库连接
docker exec -it smart_exam_pg psql -U exam -d examdb -c "\l"
```

### 权限问题
```bash
# 确保文件权限正确
chmod 644 test_data/*.sql test_data/*.csv
```

### 编码问题
```bash
# 检查文件编码
file -i test_data/*.csv

# 如需转换编码
iconv -f GBK -t UTF-8 input.csv > output.csv
```
