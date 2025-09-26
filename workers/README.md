# Worker 服务使用指南

智能试卷系统的Worker服务架构实现了任务的异步处理，包含三个核心Worker：

## 1. Worker服务架构

### 1.1 服务分工

| Worker类型 | 队列名称 | 功能描述 |
|------------|----------|----------|
| **ocr-worker** | `ocr_tasks` | 版面定位、仿射校正、OMR/OCR、题块切片 |
| **autograde-worker** | `autograde_tasks` | 客观题判分、日志回写 |
| **ingest-worker** | `ingest_tasks` | 拆题分割、OCR、候选知识点（NLP）生成 |

### 1.2 统一任务消息格式

所有Worker使用统一的TaskMessage格式：

```json
{
  "task_type": "任务类型",
  "payload": {
    "具体的任务数据": "..."
  },
  "retry_count": 0,
  "created_at": "2024-09-26T10:00:00Z"
}
```

## 2. OCR Worker (ocr-worker)

### 2.1 功能特性
- **版面定位**：自动检测试卷布局和区域
- **仿射校正**：修正图像倾斜和变形
- **OMR识别**：选择题答题区域识别
- **OCR识别**：文字内容提取
- **题块切片**：将试卷分割为独立题目

### 2.2 支持的任务类型

```json
{
  "task_type": "ocr_omr_analysis",
  "payload": {
    "exam_id": "exam_001",
    "student_id": "student_001", 
    "paper_file_url": "minio://smart-exam/uploads/answer_sheet_001.jpg",
    "page_number": 1
  }
}
```

### 2.3 处理结果示例

```json
{
  "status": "completed",
  "worker": "OCR",
  "page_analysis": {
    "orientation": "portrait",
    "regions_detected": 5,
    "omr_regions": [
      {"type": "answer_sheet", "bbox": [100, 200, 300, 400]},
      {"type": "student_info", "bbox": [100, 50, 300, 150]}
    ]
  },
  "processing_time": "2.5s"
}
```

## 3. AutoGrade Worker (autograde-worker)

### 3.1 功能特性
- **客观题判分**：单选、多选、判断题自动评分
- **答案比对**：与标准答案进行匹配
- **日志回写**：记录判分结果和过程
- **统计分析**：生成得分统计

### 3.2 支持的任务类型

```json
{
  "task_type": "objective_grading",
  "payload": {
    "exam_id": "exam_001",
    "student_id": "student_001",
    "answers": {
      "1": "A", "2": "B", "3": "C"
    },
    "answer_key": {
      "1": "A", "2": "C", "3": "C"
    }
  }
}
```

### 3.3 处理结果示例

```json
{
  "status": "completed", 
  "worker": "AutoGrade",
  "grading_result": {
    "total_questions": 20,
    "correct_answers": 15,
    "score": 75.0,
    "details": [
      {"question": 1, "answer": "A", "correct": true},
      {"question": 2, "answer": "B", "correct": false}
    ]
  }
}
```

## 4. Ingest Worker (ingest-worker)

### 4.1 功能特性
- **拆题分割**：将试卷分解为独立题目
- **OCR提取**：识别题目文本内容
- **NLP分类**：自动生成候选知识点
- **智能标注**：题目类型和难度分析

### 4.2 支持的任务类型

```json
{
  "task_type": "paper_ingestion",
  "payload": {
    "paper_id": "paper_001",
    "paper_file_url": "minio://smart-exam/papers/math_test_2024.pdf",
    "subject": "数学",
    "grade": "高三",
    "teacher_id": "teacher_001"
  }
}
```

### 4.3 处理结果示例

```json
{
  "status": "completed",
  "worker": "Ingest", 
  "ingest_result": {
    "questions_extracted": 10,
    "text_recognized": true,
    "knowledge_points": ["线性代数", "概率论", "微积分"],
    "confidence": 0.85
  }
}
```

## 5. 部署和运行

### 5.1 使用Docker部署Worker

```bash
# 进入workers目录
cd workers

# 构建Worker镜像
docker build -f Dockerfile.worker -t smart-exam-worker .

# 启动所有Worker服务
docker-compose up -d
```

### 5.2 独立运行Worker

```bash
# 设置环境变量
export WORKER_TYPE=ocr
export RABBIT_URL=amqp://guest:guest@localhost:5672/

# 启动Worker
python worker_startup.py
```

### 5.3 监控Worker状态

```bash
# 查看运行中的Worker
docker-compose ps

# 查看Worker日志
docker-compose logs ocr-worker
docker-compose logs autograde-worker  
docker-compose logs ingest-worker
```

## 6. 测试Worker服务

### 6.1 运行测试脚本

```bash
# 测试所有Worker
python test_workers.py
```

### 6.2 手动发送测试任务

```python
import json
import pika

# 连接RabbitMQ
connection = pika.BlockingConnection(
    pika.URLParameters("amqp://guest:guest@localhost:5672/")
)
channel = connection.channel()

# 发送OCR任务
task = {
    "task_type": "ocr_omr_analysis",
    "payload": {"exam_id": "test_001"}
}
channel.basic_publish(
    exchange='',
    routing_key='ocr_tasks',
    body=json.dumps(task)
)
```

## 7. 扩展和配置

### 7.1 Worker配置参数

| 环境变量 | 描述 | 默认值 |
|----------|------|---------|
| `WORKER_TYPE` | Worker类型 | `ocr` |
| `RABBIT_URL` | RabbitMQ连接地址 | `amqp://guest:guest@localhost:5672/` |
| `REDIS_URL` | Redis连接地址 | `redis://redis:6379/0` |
| `POSTGRES_URL` | PostgreSQL连接地址 | `postgresql://exam:exam@postgres:5432/examdb` |
| `MINIO_ENDPOINT` | MinIO服务地址 | `minio:9000` |

### 7.2 Worker扩容

```bash
# 增加OCR Worker实例
docker-compose up -d --scale ocr-worker=3

# 增加判分Worker实例  
docker-compose up -d --scale autograde-worker=2
```

## 8. 故障排除

### 8.1 常见问题

**Worker无法连接RabbitMQ**
- 检查RabbitMQ服务是否正常运行
- 确认连接URL和认证信息正确

**任务处理失败**
- 查看Worker日志定位具体错误
- 检查任务消息格式是否正确
- 确认依赖服务（MinIO、PostgreSQL）可用

**性能问题**
- 调整Worker并发数量
- 优化任务处理逻辑
- 增加资源分配（CPU、内存）

### 8.2 日志分析

Worker日志包含以下关键信息：
- 任务接收时间
- 处理耗时
- 成功/失败状态
- 错误详情

通过日志可以分析Worker性能和排查问题。