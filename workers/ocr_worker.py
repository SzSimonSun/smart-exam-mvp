
# workers/ocr_worker.py - OCR/OMR 识别处理器
import os
import cv2
import numpy as np
import json
import psycopg2
import requests
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging
from minio import Minio
from minio.error import S3Error
from task_manager import TaskQueue, TaskType, TaskMessage, TaskStatus

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCROMRProcessor:
    """OCR/OMR 处理器：版面定位、仿射校正、OMR/OCR、题块切片"""
    
    def __init__(self):
        # 数据库连接
        self.db_config = {
            'host': 'postgres',
            'port': 5432,
            'database': 'examdb',
            'user': 'exam',
            'password': 'exam'
        }
        
        # MinIO 配置
        self.minio_client = Minio(
            "minio:9000",
            access_key="minio",
            secret_key="minio123",
            secure=False
        )
        
        # 确保存储桶存在
        try:
            if not self.minio_client.bucket_exists("smart-exam"):
                self.minio_client.make_bucket("smart-exam")
        except S3Error as e:
            logger.error(f"MinIO bucket 操作失败: {e}")
    
    def download_file_from_minio(self, file_uri: str) -> str:
        """从 MinIO 下载文件到本地"""
        try:
            # 解析文件路径
            bucket_name = "smart-exam"
            object_name = file_uri.split('/')[-1]
            local_path = f"/tmp/{object_name}"
            
            # 下载文件
            self.minio_client.fget_object(bucket_name, object_name, local_path)
            logger.info(f"文件已下载到: {local_path}")
            return local_path
        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            raise
    
    def detect_paper_layout(self, image: np.ndarray) -> Dict[str, Any]:
        """版面检测和定位"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 二值化
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 查找轮廓
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 找到最大的矩形轮廓（试卷边界）
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 获取边界框
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # 检测QR码区域（简化实现）
            qr_regions = self._detect_qr_codes(gray)
            
            layout_info = {
                "paper_bounds": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "qr_codes": qr_regions,
                "detected_at": datetime.utcnow().isoformat()
            }
            
            logger.info("版面检测完成")
            return layout_info
            
        except Exception as e:
            logger.error(f"版面检测失败: {e}")
            return {"error": str(e)}
    
    def _detect_qr_codes(self, gray_image: np.ndarray) -> List[Dict[str, int]]:
        """检测QR码区域（简化实现）"""
        # 这里应该使用专门的QR码检测库，为了MVP先返回模拟结果
        height, width = gray_image.shape
        return [
            {
                "x": int(width * 0.8),
                "y": int(height * 0.05),
                "width": int(width * 0.15),
                "height": int(height * 0.1),
                "content": 123456
            }
        ]
    
    def correct_affine_transformation(self, image: np.ndarray, layout_info: Dict[str, Any]) -> np.ndarray:
        """仿射变换校正"""
        try:
            # 获取试卷边界
            bounds = layout_info["paper_bounds"]
            x, y, w, h = bounds["x"], bounds["y"], bounds["width"], bounds["height"]
            
            # 裁剪试卷区域
            cropped = image[y:y+h, x:x+w]
            
            # 简化的校正：调整大小到标准尺寸
            standard_height, standard_width = 1200, 800
            corrected = cv2.resize(cropped, (standard_width, standard_height))
            
            logger.info("仿射变换校正完成")
            return corrected
            
        except Exception as e:
            logger.error(f"仿射变换校正失败: {e}")
            return image
    
    def extract_omr_data(self, image: np.ndarray) -> Dict[str, Any]:
        """OMR光学标记识别"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 模拟OMR检测结果
            omr_results = {
                "student_id": "202301001",
                "answers": {
                    "1": {"marked": ["A"], "confidence": 0.95},
                    "2": {"marked": ["B"], "confidence": 0.88},
                    "3": {"marked": ["C"], "confidence": 0.92},
                    "4": {"marked": ["A", "C"], "confidence": 0.76},  # 多选题
                    "5": {"marked": ["B"], "confidence": 0.94}
                },
                "quality_issues": [
                    {"question": 4, "issue": "MULTI_MARK", "severity": "medium"}
                ],
                "processed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"OMR识别完成，检测到 {len(omr_results['answers'])} 道题的答案")
            return omr_results
            
        except Exception as e:
            logger.error(f"OMR识别失败: {e}")
            return {"error": str(e)}
    
    def extract_ocr_data(self, image: np.ndarray) -> Dict[str, Any]:
        """OCR文字识别"""
        try:
            # 模拟OCR识别结果（主观题和填空题）
            ocr_results = {
                "subjective_answers": {
                    "21": {
                        "text": "根据勾股定理，直角三角形的两直角边的平方和等于斜边的平方。",
                        "confidence": 0.85,
                        "bounding_box": {"x": 100, "y": 800, "width": 600, "height": 120}
                    },
                    "22": {
                        "text": "解：设直角边为a、b，斜边为c，则a²+b²=c²",
                        "confidence": 0.78,
                        "bounding_box": {"x": 100, "y": 950, "width": 600, "height": 80}
                    }
                },
                "fill_answers": {
                    "15": {"text": "25", "confidence": 0.92},
                    "16": {"text": "π", "confidence": 0.67},
                    "17": {"text": "x=3", "confidence": 0.89}
                },
                "processed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"OCR识别完成，识别了 {len(ocr_results['subjective_answers'])} 道主观题")
            return ocr_results
            
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return {"error": str(e)}
    
    def update_database(self, task: TaskMessage, results: Dict[str, Any]) -> bool:
        """更新数据库结果"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            sheet_id = task.payload["sheet_id"]
            
            # 更新答题卡状态
            cur.execute(
                "UPDATE answer_sheets SET status = %s WHERE id = %s",
                ("processed", sheet_id)
            )
            
            # 插入识别结果到answers表
            if "omr_results" in results and "answers" in results["omr_results"]:
                for q_num, answer_data in results["omr_results"]["answers"].items():
                    cur.execute(
                        """
                        INSERT INTO answers (sheet_id, question_id, raw_omr, raw_ocr, 
                                           parsed_json, is_objective, error_flag)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (sheet_id, question_id) 
                        DO UPDATE SET raw_omr = %s, parsed_json = %s
                        """,
                        (
                            sheet_id, int(q_num), json.dumps(answer_data),
                            None, json.dumps(answer_data["marked"]),
                            True, False,
                            json.dumps(answer_data), json.dumps(answer_data["marked"])
                        )
                    )
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"数据库更新完成，答题卡 {sheet_id}")
            return True
            
        except Exception as e:
            logger.error(f"数据库更新失败: {e}")
            return False
    
    def send_callback(self, task: TaskMessage, results: Dict[str, Any]) -> bool:
        """发送处理结果回调"""
        try:
            callback_url = "http://backend:8000/internal/ocr-omr/callback"
            
            payload = {
                "task_id": task.task_id,
                "sheet_id": task.payload["sheet_id"],
                "status": "completed" if "error" not in results else "failed",
                "results": results,
                "processed_at": datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                callback_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"回调发送成功，任务 {task.task_id}")
                return True
            else:
                logger.error(f"回调发送失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"发送回调失败: {e}")
            return False
    
    def process_task(self, task: TaskMessage) -> bool:
        """处理OCR/OMR任务"""
        try:
            logger.info(f"开始处理OCR/OMR任务 {task.task_id}")
            
            # 下载文件
            local_file_path = self.download_file_from_minio(task.payload["file_uri"])
            
            # 读取图像
            image = cv2.imread(local_file_path)
            if image is None:
                raise ValueError("无法读取图像文件")
            
            results = {}
            
            # 1. 版面检测
            layout_info = self.detect_paper_layout(image)
            results["layout_info"] = layout_info
            
            # 2. 仿射校正
            corrected_image = self.correct_affine_transformation(image, layout_info)
            
            # 3. OMR识别
            omr_results = self.extract_omr_data(corrected_image)
            results["omr_results"] = omr_results
            
            # 4. OCR识别
            ocr_results = self.extract_ocr_data(corrected_image)
            results["ocr_results"] = ocr_results
            
            # 5. 更新数据库
            db_success = self.update_database(task, results)
            
            # 6. 发送回调
            callback_success = self.send_callback(task, results)
            
            # 清理临时文件
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
            
            success = db_success and callback_success
            logger.info(f"OCR/OMR任务 {task.task_id} 处理{'成功' if success else '失败'}")
            return success
            
        except Exception as e:
            logger.error(f"处理OCR/OMR任务失败: {e}")
            return False

def main():
    """OCR/OMR Worker 主函数"""
    logger.info("启动 OCR/OMR Worker")
    
    processor = OCROMRProcessor()
    task_queue = TaskQueue()
    
    try:
        # 开始消费任务
        task_queue.consume_tasks(
            TaskType.OCR_OMR,
            processor.process_task
        )
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭...")
    except Exception as e:
        logger.error(f"Worker运行出错: {e}")
    finally:
        task_queue.close()
        logger.info("OCR/OMR Worker 已停止")

if __name__ == "__main__":
    main()
