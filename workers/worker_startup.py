#!/usr/bin/env python3
# workers/worker_startup.py - Worker服务启动脚本

import os
import sys
import logging
import pika
import json
import signal
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 获取Worker类型
WORKER_TYPE = os.getenv("WORKER_TYPE", "ocr")
RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@localhost:5672/")

class SimpleWorker:
    """简化的Worker基类"""
    
    def __init__(self, worker_type: str, queue_name: str):
        self.worker_type = worker_type
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.running = False
    
    def connect(self):
        """连接到RabbitMQ"""
        try:
            params = pika.URLParameters(RABBIT_URL)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            
            # 声明队列
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.channel.basic_qos(prefetch_count=1)
            
            logger.info(f"{self.worker_type} Worker 已连接到 RabbitMQ")
            
        except Exception as e:
            logger.error(f"连接 RabbitMQ 失败: {e}")
            raise
    
    def process_message(self, ch, method, properties, body):
        """处理消息"""
        try:
            # 解析任务消息
            task_data = json.loads(body.decode('utf-8'))
            logger.info(f"收到 {self.worker_type} 任务: {task_data}")
            
            # 调用处理方法
            result = self.handle_task(task_data)
            
            # 确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"{self.worker_type} 任务处理完成: {result}")
            
        except Exception as e:
            logger.error(f"{self.worker_type} 任务处理失败: {e}")
            # 拒绝消息，不重新入队
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def handle_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理具体任务 - 子类需要重写此方法"""
        return {"status": "completed", "worker": self.worker_type}
    
    def start(self):
        """启动Worker"""
        self.connect()
        self.running = True
        
        if not self.channel:
            raise RuntimeError("频道未连接")
        
        # 设置消息处理回调
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.process_message
        )
        
        logger.info(f"{self.worker_type} Worker 开始监听任务...")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info(f"{self.worker_type} Worker 收到停止信号")
            self.stop()
    
    def stop(self):
        """停止Worker"""
        self.running = False
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()
        logger.info(f"{self.worker_type} Worker 已停止")

class OCRWorker(SimpleWorker):
    """OCR/OMR Worker"""
    
    def __init__(self):
        super().__init__("OCR", "ocr_tasks")
    
    def handle_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理OCR任务"""
        logger.info("执行版面定位、仿射校正、OMR/OCR、题块切片...")
        
        # 模拟OCR处理
        result = {
            "status": "completed",
            "worker": "OCR",
            "task_type": task_data.get("task_type", "unknown"),
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
        
        return result

class AutoGradeWorker(SimpleWorker):
    """自动判分Worker"""
    
    def __init__(self):
        super().__init__("AutoGrade", "autograde_tasks")
    
    def handle_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理判分任务"""
        logger.info("执行客观题判分、日志回写...")
        
        # 模拟判分处理
        result = {
            "status": "completed",
            "worker": "AutoGrade",
            "task_type": task_data.get("task_type", "unknown"),
            "grading_result": {
                "total_questions": 20,
                "correct_answers": 15,
                "score": 75.0,
                "details": [
                    {"question": 1, "answer": "A", "correct": True},
                    {"question": 2, "answer": "B", "correct": False},
                ]
            },
            "processing_time": "1.2s"
        }
        
        return result

class IngestWorker(SimpleWorker):
    """拆题入库Worker"""
    
    def __init__(self):
        super().__init__("Ingest", "ingest_tasks")
    
    def handle_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理拆题任务"""
        logger.info("执行拆题分割、OCR、候选知识点（NLP）生成...")
        
        # 模拟拆题处理
        result = {
            "status": "completed",
            "worker": "Ingest",
            "task_type": task_data.get("task_type", "unknown"),
            "ingest_result": {
                "questions_extracted": 10,
                "text_recognized": True,
                "knowledge_points": ["线性代数", "概率论", "微积分"],
                "confidence": 0.85
            },
            "processing_time": "3.8s"
        }
        
        return result

# 全局Worker实例
worker = None

def signal_handler(signum, frame):
    """信号处理器"""
    global worker
    logger.info(f"收到信号 {signum}，准备停止Worker...")
    if worker:
        worker.stop()
    sys.exit(0)

def main():
    """主函数"""
    global worker
    logger.info(f"=== 启动 {WORKER_TYPE} Worker 服务 ===")
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 创建对应的Worker实例
    if WORKER_TYPE.lower() == "ocr":
        worker = OCRWorker()
    elif WORKER_TYPE.lower() == "autograde":
        worker = AutoGradeWorker()
    elif WORKER_TYPE.lower() == "ingest":
        worker = IngestWorker()
    else:
        logger.error(f"未知的Worker类型: {WORKER_TYPE}")
        sys.exit(1)
    
    try:
        # 启动Worker
        worker.start()
    except Exception as e:
        logger.error(f"Worker启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()