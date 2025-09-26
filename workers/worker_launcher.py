#!/usr/bin/env python3
# workers/worker_launcher.py - Worker启动器

import asyncio
import threading
import signal
import sys
import logging
from typing import List

from task_manager import TaskQueue, TaskType
from ocr_worker import OCROMRProcessor
from omr_worker import AutoGradeProcessor  
from ingest_worker import IngestProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

class WorkerManager:
    """Worker管理器：统一管理三个Worker服务"""
    
    def __init__(self):
        self.workers = []
        self.running = False
        
        # 创建Worker实例
        self.ocr_processor = OCROMRProcessor()
        self.grade_processor = AutoGradeProcessor()
        self.ingest_processor = IngestProcessor()
        
        # 创建任务队列
        self.ocr_queue = TaskQueue("ocr_tasks", "amqp://guest:guest@localhost:5672/")
        self.grade_queue = TaskQueue("autograde_tasks", "amqp://guest:guest@localhost:5672/")
        self.ingest_queue = TaskQueue("ingest_tasks", "amqp://guest:guest@localhost:5672/")
    
    def start_workers(self):
        """启动所有Worker"""
        logger.info("启动Worker服务...")
        self.running = True
        
        # 启动OCR Worker线程
        ocr_thread = threading.Thread(
            target=self._run_ocr_worker,
            name="OCR-Worker"
        )
        ocr_thread.daemon = True
        ocr_thread.start()
        self.workers.append(ocr_thread)
        
        # 启动判分Worker线程
        grade_thread = threading.Thread(
            target=self._run_grade_worker,
            name="AutoGrade-Worker"
        )
        grade_thread.daemon = True
        grade_thread.start()
        self.workers.append(grade_thread)
        
        # 启动拆题Worker线程
        ingest_thread = threading.Thread(
            target=self._run_ingest_worker,
            name="Ingest-Worker"
        )
        ingest_thread.daemon = True
        ingest_thread.start()
        self.workers.append(ingest_thread)
        
        logger.info(f"已启动 {len(self.workers)} 个Worker线程")
    
    def _run_ocr_worker(self):
        """运行OCR Worker"""
        try:
            logger.info("OCR Worker 开始监听任务...")
            self.ocr_queue.start_consuming(self._handle_ocr_task)
        except Exception as e:
            logger.error(f"OCR Worker 异常: {e}")
    
    def _run_grade_worker(self):
        """运行判分Worker"""
        try:
            logger.info("AutoGrade Worker 开始监听任务...")
            self.grade_queue.start_consuming(self._handle_grade_task)
        except Exception as e:
            logger.error(f"AutoGrade Worker 异常: {e}")
    
    def _run_ingest_worker(self):
        """运行拆题Worker"""
        try:
            logger.info("Ingest Worker 开始监听任务...")
            self.ingest_queue.start_consuming(self._handle_ingest_task)
        except Exception as e:
            logger.error(f"Ingest Worker 异常: {e}")
    
    def _handle_ocr_task(self, task_data: dict):
        """处理OCR任务"""
        try:
            logger.info(f"处理OCR任务: {task_data}")
            
            # 使用OCR处理器处理任务
            result = asyncio.run(
                self.ocr_processor.process_ocr_task(task_data)
            )
            
            logger.info(f"OCR任务处理完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"OCR任务处理失败: {e}")
            raise
    
    def _handle_grade_task(self, task_data: dict):
        """处理判分任务"""
        try:
            logger.info(f"处理判分任务: {task_data}")
            
            # 使用判分处理器处理任务
            result = asyncio.run(
                self.grade_processor.process_grade_task(task_data)
            )
            
            logger.info(f"判分任务处理完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"判分任务处理失败: {e}")
            raise
    
    def _handle_ingest_task(self, task_data: dict):
        """处理拆题任务"""
        try:
            logger.info(f"处理拆题任务: {task_data}")
            
            # 使用拆题处理器处理任务
            result = asyncio.run(
                self.ingest_processor.process_ingest_task(task_data)
            )
            
            logger.info(f"拆题任务处理完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"拆题任务处理失败: {e}")
            raise
    
    def stop_workers(self):
        """停止所有Worker"""
        logger.info("停止Worker服务...")
        self.running = False
        
        # 关闭队列连接
        try:
            self.ocr_queue.close()
            self.grade_queue.close()
            self.ingest_queue.close()
        except Exception as e:
            logger.error(f"关闭队列连接失败: {e}")
        
        logger.info("所有Worker已停止")

def signal_handler(signum, frame):
    """信号处理器"""
    logger.info(f"收到信号 {signum}，准备停止Worker...")
    worker_manager.stop_workers()
    sys.exit(0)

# 全局Worker管理器实例
worker_manager = WorkerManager()

def main():
    """主函数"""
    logger.info("=== 智能试卷系统 Worker 服务启动 ===")
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动Worker服务
        worker_manager.start_workers()
        
        # 保持主线程运行
        logger.info("Worker服务运行中，按 Ctrl+C 退出...")
        while True:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("收到键盘中断，停止Worker服务...")
        worker_manager.stop_workers()
    except Exception as e:
        logger.error(f"Worker服务异常: {e}")
        worker_manager.stop_workers()
    finally:
        logger.info("Worker服务已退出")

if __name__ == "__main__":
    main()