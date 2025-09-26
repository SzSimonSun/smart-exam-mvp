
# workers/ingest_worker.py - 拆题入库处理器
import os
import cv2
import numpy as np
import json
import psycopg2
import requests
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging
from minio import Minio
from minio.error import S3Error
from task_manager import TaskQueue, TaskType, TaskMessage, TaskStatus

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IngestProcessor:
    """拆题入库处理器：拆题分割、OCR、候选知识点（NLP）生成"""
    
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
            bucket_name = "smart-exam"
            object_name = file_uri.split('/')[-1]
            local_path = f"/tmp/{object_name}"
            
            self.minio_client.fget_object(bucket_name, object_name, local_path)
            logger.info(f"文件已下载到: {local_path}")
            return local_path
        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            raise
    
    def analyze_layout(self, image: np.ndarray) -> Dict[str, Any]:
        """版面布局分析"""
        try:
            height, width = image.shape[:2]
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 二值化
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 模拟版面分析结果
            layout_info = {
                "page_size": {"width": width, "height": height},
                "orientation": "portrait" if height > width else "landscape",
                "detected_regions": [
                    {
                        "type": "header",
                        "bbox": {"x": 0, "y": 0, "width": width, "height": int(height * 0.1)}
                    },
                    {
                        "type": "content", 
                        "bbox": {"x": 0, "y": int(height * 0.1), "width": width, "height": int(height * 0.8)}
                    },
                    {
                        "type": "footer",
                        "bbox": {"x": 0, "y": int(height * 0.9), "width": width, "height": int(height * 0.1)}
                    }
                ],
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            logger.info("版面布局分析完成")
            return layout_info
            
        except Exception as e:
            logger.error(f"版面布局分析失败: {e}")
            return {"error": str(e)}
    
    def segment_questions(self, image: np.ndarray, layout_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """题目分割和提取"""
        try:
            height, width = image.shape[:2]
            
            # 模拟题目分割（假设每页有10道题）
            questions_per_page = 10
            content_region = None
            
            # 找到内容区域
            for region in layout_info.get("detected_regions", []):
                if region["type"] == "content":
                    content_region = region["bbox"]
                    break
            
            if not content_region:
                content_region = {"x": 0, "y": int(height * 0.1), "width": width, "height": int(height * 0.8)}
            
            # 分割题目
            question_height = content_region["height"] // questions_per_page
            questions = []
            
            for i in range(questions_per_page):
                y_start = content_region["y"] + i * question_height
                y_end = min(y_start + question_height, content_region["y"] + content_region["height"])
                
                # 提取题目区域
                question_image = image[y_start:y_end, content_region["x"]:content_region["x"] + content_region["width"]]
                
                # 保存题目图片
                crop_filename = f"ingest_question_{i+1}.jpg"
                crop_path = f"/tmp/{crop_filename}"
                cv2.imwrite(crop_path, question_image)
                
                # 上传到MinIO
                crop_uri = None
                try:
                    self.minio_client.fput_object(
                        "smart-exam",
                        f"ingest/{crop_filename}",
                        crop_path
                    )
                    crop_uri = f"minio://smart-exam/ingest/{crop_filename}"
                except Exception as e:
                    logger.warning(f"上传题目图片失败: {e}")
                
                questions.append({
                    "seq": i + 1,
                    "bbox": {
                        "x": content_region["x"],
                        "y": y_start,
                        "width": content_region["width"],
                        "height": y_end - y_start
                    },
                    "crop_uri": crop_uri
                })
            
            logger.info(f"题目分割完成，共分割 {len(questions)} 道题")
            return questions
            
        except Exception as e:
            logger.error(f"题目分割失败: {e}")
            return []
    
    def extract_question_text(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取题目文本（OCR）"""
        try:
            # 模拟OCR提取结果
            seq = question_data["seq"]
            
            # 模拟不同类型的题目
            if seq <= 5:  # 单选题
                ocr_result = {
                    "stem": f"第{seq}题：下列哪个选项是正确的？",
                    "options": {
                        "A": f"选项A的内容{seq}",
                        "B": f"选项B的内容{seq}",
                        "C": f"选项C的内容{seq}",
                        "D": f"选项D的内容{seq}"
                    },
                    "type": "single",
                    "confidence": 0.85 + seq * 0.02
                }
            elif seq <= 8:  # 多选题
                ocr_result = {
                    "stem": f"第{seq}题：下列选项中正确的有（多选）？",
                    "options": {
                        "A": f"选项A的内容{seq}",
                        "B": f"选项B的内容{seq}",
                        "C": f"选项C的内容{seq}",
                        "D": f"选项D的内容{seq}"
                    },
                    "type": "multiple",
                    "confidence": 0.82 + seq * 0.01
                }
            else:  # 主观题
                ocr_result = {
                    "stem": f"第{seq}题：请简述相关概念和原理。",
                    "type": "subjective",
                    "confidence": 0.78 + seq * 0.02
                }
            
            logger.info(f"题目 {seq} 的OCR提取完成")
            return ocr_result
            
        except Exception as e:
            logger.error(f"题目OCR提取失败: {e}")
            return {"error": str(e)}
    
    def classify_knowledge_points(self, ocr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """智能分类知识点（NLP）"""
        try:
            stem = ocr_data.get("stem", "")
            question_type = ocr_data.get("type", "single")
            
            # 模拟NLP分类结果
            candidate_kps = []
            
            # 根据题目内容进行简单的关键词匹配
            if "数学" in stem or "计算" in stem or "公式" in stem:
                candidate_kps.extend([
                    {"id": 1, "code": "MATH_ALG_QUAD_ROOT", "confidence": 0.85},
                    {"id": 2, "code": "MATH_ALG_QUAD_DISC", "confidence": 0.72}
                ])
            elif "三角" in stem or "几何" in stem:
                candidate_kps.append(
                    {"id": 3, "code": "MATH_GEO_TRI_PYTH", "confidence": 0.88}
                )
            elif "语文" in stem or "阅读" in stem:
                candidate_kps.append(
                    {"id": 4, "code": "LANG_READ_MAIN_IDEA", "confidence": 0.79}
                )
            elif "英语" in stem or "English" in stem:
                candidate_kps.append(
                    {"id": 5, "code": "ENG_GRAM_PAST_TENSE", "confidence": 0.76}
                )
            else:
                # 默认分类
                candidate_kps.append(
                    {"id": 1, "code": "MATH_ALG_QUAD_ROOT", "confidence": 0.65}
                )
            
            # 根据题型调整置信度
            if question_type == "subjective":
                for kp in candidate_kps:
                    kp["confidence"] *= 0.9  # 主观题的置信度略低
            
            logger.info(f"知识点分类完成，候选知识点: {len(candidate_kps)} 个")
            return candidate_kps
            
        except Exception as e:
            logger.error(f"知识点分类失败: {e}")
            return []
    
    def save_ingest_items(self, session_id: int, questions_data: List[Dict[str, Any]]) -> bool:
        """保存拆题结果到数据库"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            for question_data in questions_data:
                seq = question_data["seq"]
                crop_uri = question_data.get("crop_uri")
                ocr_data = question_data.get("ocr_result", {})
                candidate_kps = question_data.get("candidate_kps", [])
                
                # 计算综合置信度
                avg_confidence = sum([kp["confidence"] for kp in candidate_kps]) / len(candidate_kps) if candidate_kps else 0.5
                
                # 插入拆题项目
                cur.execute(
                    """
                    INSERT INTO ingest_items 
                    (session_id, seq, crop_uri, ocr_json, candidate_type, candidate_kps_json, confidence, review_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
                    """,
                    (
                        session_id,
                        seq,
                        crop_uri,
                        json.dumps(ocr_data),
                        ocr_data.get("type", "single"),
                        json.dumps(candidate_kps),
                        avg_confidence
                    )
                )
            
            # 更新会话状态
            cur.execute(
                "UPDATE ingest_sessions SET status = 'awaiting_review' WHERE id = %s",
                (session_id,)
            )
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"会话 {session_id} 的拆题结果已保存，共 {len(questions_data)} 道题")
            return True
            
        except Exception as e:
            logger.error(f"保存拆题结果失败: {e}")
            return False
    
    def process_task(self, task: TaskMessage) -> bool:
        """处理拆题入库任务"""
        try:
            logger.info(f"开始处理拆题入库任务 {task.task_id}")
            
            session_id = task.payload["session_id"]
            file_uri = task.payload["file_uri"]
            uploader_id = task.payload["uploader_id"]
            
            # 下载文件
            local_file_path = self.download_file_from_minio(file_uri)
            
            # 读取图像
            image = cv2.imread(local_file_path)
            if image is None:
                raise ValueError("无法读取图像文件")
            
            # 1. 版面布局分析
            layout_info = self.analyze_layout(image)
            
            # 2. 题目分割
            questions = self.segment_questions(image, layout_info)
            
            # 3. OCR提取和知识点分类
            questions_data = []
            for question in questions:
                # OCR提取
                ocr_result = self.extract_question_text(question)
                
                # 知识点分类
                candidate_kps = self.classify_knowledge_points(ocr_result)
                
                questions_data.append({
                    "seq": question["seq"],
                    "bbox": question["bbox"],
                    "crop_uri": question.get("crop_uri"),
                    "ocr_result": ocr_result,
                    "candidate_kps": candidate_kps
                })
            
            # 4. 保存结果到数据库
            save_success = self.save_ingest_items(session_id, questions_data)
            
            # 清理临时文件
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
            
            if save_success:
                logger.info(f"拆题入库任务 {task.task_id} 处理成功")
                return True
            else:
                logger.error(f"拆题入库任务 {task.task_id} 处理失败")
                return False
                
        except Exception as e:
            logger.error(f"处理拆题入库任务失败: {e}")
            return False

def main():
    """Ingest Worker 主函数"""
    logger.info("启动拆题入库 Worker")
    
    processor = IngestProcessor()
    task_queue = TaskQueue()
    
    try:
        # 开始消费任务
        task_queue.consume_tasks(
            TaskType.INGEST,
            processor.process_task
        )
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭...")
    except Exception as e:
        logger.error(f"Worker运行出错: {e}")
    finally:
        task_queue.close()
        logger.info("拆题入库 Worker 已停止")

if __name__ == "__main__":
    main()
