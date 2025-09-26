# workers/task_manager.py - 统一任务消息格式和队列管理
import json
import pika
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(str, Enum):
    """任务类型枚举"""
    OCR_OMR = "ocr_omr"           # OCR/OMR识别任务
    AUTO_GRADE = "auto_grade"     # 自动判分任务  
    INGEST = "ingest"             # 拆题入库任务

class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

class TaskMessage:
    """统一任务消息格式"""
    
    def __init__(
        self,
        task_type: TaskType,
        payload: Dict[str, Any],
        task_id: Optional[str] = None,
        retry_count: int = 0,
        max_retries: int = 3,
        priority: int = 5,
        timeout_seconds: int = 300
    ):
        self.task_id = task_id or str(uuid.uuid4())
        self.task_type = task_type
        self.payload = payload
        self.retry_count = retry_count
        self.max_retries = max_retries
        self.priority = priority
        self.timeout_seconds = timeout_seconds
        self.created_at = datetime.utcnow().isoformat()
        self.status = TaskStatus.PENDING
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "payload": self.payload,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "priority": self.priority,
            "timeout_seconds": self.timeout_seconds,
            "created_at": self.created_at,
            "status": self.status
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskMessage':
        """从字典创建任务消息"""
        task = cls(
            task_type=data["task_type"],
            payload=data["payload"],
            task_id=data.get("task_id"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            priority=data.get("priority", 5),
            timeout_seconds=data.get("timeout_seconds", 300)
        )
        task.created_at = data.get("created_at", task.created_at)
        task.status = data.get("status", TaskStatus.PENDING)
        return task
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TaskMessage':
        """从JSON字符串创建任务消息"""
        return cls.from_dict(json.loads(json_str))

class TaskQueue:
    """RabbitMQ 任务队列管理器"""
    
    def __init__(self, rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672//"):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        self.connect()
        
    def connect(self):
        """连接到RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            self.channel = self.connection.channel()
            self._declare_queues()
            logger.info("成功连接到RabbitMQ")
        except Exception as e:
            logger.error(f"连接RabbitMQ失败: {e}")
            raise
            
    def _declare_queues(self):
        """声明队列和交换机"""
        # 主要工作队列
        queues = [
            "ocr_omr_queue",      # OCR/OMR处理队列
            "auto_grade_queue",   # 自动判分队列
            "ingest_queue",       # 拆题入库队列
        ]
        
        # 死信队列
        dlq_queues = [
            "ocr_omr_dlq",
            "auto_grade_dlq", 
            "ingest_dlq"
        ]
        
        # 声明工作队列
        for queue in queues:
            self.channel.queue_declare(
                queue=queue,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': '',
                    'x-dead-letter-routing-key': f"{queue.replace('_queue', '_dlq')}"
                }
            )
            
        # 声明死信队列
        for dlq in dlq_queues:
            self.channel.queue_declare(
                queue=dlq,
                durable=True
            )
            
    def publish_task(self, task: TaskMessage) -> bool:
        """发布任务到队列"""
        try:
            # 根据任务类型选择队列
            queue_map = {
                TaskType.OCR_OMR: "ocr_omr_queue",
                TaskType.AUTO_GRADE: "auto_grade_queue", 
                TaskType.INGEST: "ingest_queue"
            }
            
            queue_name = queue_map.get(task.task_type)
            if not queue_name:
                raise ValueError(f"未知的任务类型: {task.task_type}")
                
            # 发布消息
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=task.to_json(),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 持久化消息
                    priority=task.priority,
                    message_id=task.task_id,
                    timestamp=int(time.time())
                )
            )
            
            logger.info(f"任务 {task.task_id} 已发布到队列 {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"发布任务失败: {e}")
            return False
    
    def consume_tasks(self, task_type: TaskType, callback_func):
        """消费指定类型的任务"""
        queue_map = {
            TaskType.OCR_OMR: "ocr_omr_queue",
            TaskType.AUTO_GRADE: "auto_grade_queue",
            TaskType.INGEST: "ingest_queue"
        }
        
        queue_name = queue_map.get(task_type)
        if not queue_name:
            raise ValueError(f"未知的任务类型: {task_type}")
            
        def wrapper(ch, method, properties, body):
            """包装回调函数"""
            try:
                task = TaskMessage.from_json(body.decode('utf-8'))
                logger.info(f"开始处理任务 {task.task_id}")
                
                # 调用具体的处理函数
                result = callback_func(task)
                
                if result:
                    # 任务成功，确认消息
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"任务 {task.task_id} 处理成功")
                else:
                    # 任务失败，检查重试次数
                    if task.retry_count < task.max_retries:
                        # 重新排队重试
                        task.retry_count += 1
                        task.status = TaskStatus.RETRY
                        self.publish_task(task)
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        logger.warning(f"任务 {task.task_id} 重试第 {task.retry_count} 次")
                    else:
                        # 超过重试次数，发送到死信队列
                        ch.basic_nack(
                            delivery_tag=method.delivery_tag, 
                            requeue=False
                        )
                        logger.error(f"任务 {task.task_id} 超过最大重试次数，发送到死信队列")
                        
            except Exception as e:
                logger.error(f"处理任务时发生错误: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        # 设置 QoS
        self.channel.basic_qos(prefetch_count=1)
        
        # 开始消费
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=wrapper
        )
        
        logger.info(f"开始消费队列 {queue_name}")
        self.channel.start_consuming()
    
    def close(self):
        """关闭连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ连接已关闭")

# 任务工厂函数
def create_ocr_omr_task(
    sheet_id: int,
    file_uri: str,
    paper_id: int,
    student_id: int,
    class_id: int
) -> TaskMessage:
    """创建OCR/OMR识别任务"""
    payload = {
        "sheet_id": sheet_id,
        "file_uri": file_uri,
        "paper_id": paper_id,
        "student_id": student_id,
        "class_id": class_id,
        "operations": ["layout_detection", "affine_correction", "omr_extraction", "ocr_extraction"]
    }
    return TaskMessage(TaskType.OCR_OMR, payload)

def create_auto_grade_task(
    sheet_id: int,
    answers: List[Dict[str, Any]]
) -> TaskMessage:
    """创建自动判分任务"""
    payload = {
        "sheet_id": sheet_id, 
        "answers": answers,
        "grade_objective_only": True
    }
    return TaskMessage(TaskType.AUTO_GRADE, payload)

def create_ingest_task(
    session_id: int,
    file_uri: str,
    uploader_id: int
) -> TaskMessage:
    """创建拆题入库任务"""
    payload = {
        "session_id": session_id,
        "file_uri": file_uri,
        "uploader_id": uploader_id,
        "operations": ["layout_analysis", "question_segmentation", "ocr_extraction", "nlp_classification"]
    }
    return TaskMessage(TaskType.INGEST, payload)