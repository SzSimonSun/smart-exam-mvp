#!/usr/bin/env python3
# workers/test_workers.py - Worker服务测试脚本

import json
import pika
import logging
import time
from typing import Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkerTester:
    """Worker服务测试器"""
    
    def __init__(self, rabbit_url: str = "amqp://guest:guest@localhost:5672/"):
        self.rabbit_url = rabbit_url
        self.connection = None
        self.channel = None
    
    def connect(self):
        """连接到RabbitMQ"""
        try:
            params = pika.URLParameters(self.rabbit_url)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            logger.info("已连接到RabbitMQ")
        except Exception as e:
            logger.error(f"连接RabbitMQ失败: {e}")
            raise
    
    def send_task(self, queue_name: str, task_data: Dict[str, Any]):
        """发送任务到指定队列"""
        try:
            if not self.channel:
                self.connect()
            
            # 声明队列
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # 发送消息
            message = json.dumps(task_data)
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 消息持久化
                )
            )
            
            logger.info(f"已发送任务到队列 {queue_name}: {task_data}")
            
        except Exception as e:
            logger.error(f"发送任务失败: {e}")
            raise
    
    def test_ocr_worker(self):
        """测试OCR Worker"""
        logger.info("=== 测试OCR Worker ===")
        
        task_data = {
            "task_type": "ocr_omr_analysis",
            "payload": {
                "exam_id": "exam_001",
                "student_id": "student_001",
                "paper_file_url": "minio://smart-exam/uploads/answer_sheet_001.jpg",
                "page_number": 1
            },
            "retry_count": 0,
            "created_at": "2024-09-26T10:00:00Z"
        }
        
        self.send_task("ocr_tasks", task_data)
    
    def test_autograde_worker(self):
        """测试自动判分Worker"""
        logger.info("=== 测试AutoGrade Worker ===")
        
        task_data = {
            "task_type": "objective_grading",
            "payload": {
                "exam_id": "exam_001",
                "student_id": "student_001",
                "answers": {
                    "1": "A",
                    "2": "B", 
                    "3": "C",
                    "4": "D",
                    "5": "A"
                },
                "answer_key": {
                    "1": "A",
                    "2": "C",
                    "3": "C", 
                    "4": "D",
                    "5": "B"
                }
            },
            "retry_count": 0,
            "created_at": "2024-09-26T10:00:00Z"
        }
        
        self.send_task("autograde_tasks", task_data)
    
    def test_ingest_worker(self):
        """测试拆题入库Worker"""
        logger.info("=== 测试Ingest Worker ===")
        
        task_data = {
            "task_type": "paper_ingestion",
            "payload": {
                "paper_id": "paper_001",
                "paper_file_url": "minio://smart-exam/papers/math_test_2024.pdf",
                "subject": "数学",
                "grade": "高三",
                "teacher_id": "teacher_001"
            },
            "retry_count": 0,
            "created_at": "2024-09-26T10:00:00Z"
        }
        
        self.send_task("ingest_tasks", task_data)
    
    def run_all_tests(self):
        """运行所有Worker测试"""
        logger.info("=== 开始Worker服务测试 ===")
        
        try:
            self.connect()
            
            # 测试各个Worker
            self.test_ocr_worker()
            time.sleep(1)
            
            self.test_autograde_worker() 
            time.sleep(1)
            
            self.test_ingest_worker()
            
            logger.info("=== 所有测试任务已发送 ===")
            
        except Exception as e:
            logger.error(f"测试失败: {e}")
        finally:
            if self.connection:
                self.connection.close()
                logger.info("已关闭RabbitMQ连接")

def main():
    """主函数"""
    tester = WorkerTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()