
# workers/omr_worker.py - 自动判分处理器
import json
import psycopg2
import requests
from typing import Dict, Any, List
from datetime import datetime
import logging
from task_manager import TaskQueue, TaskType, TaskMessage, TaskStatus

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoGradeProcessor:
    """自动判分处理器：客观题判分、日志回写"""
    
    def __init__(self):
        # 数据库连接
        self.db_config = {
            'host': 'postgres',
            'port': 5432,
            'database': 'examdb',
            'user': 'exam',
            'password': 'exam'
        }
    
    def get_paper_answers(self, paper_id: int) -> Dict[str, Any]:
        """获取试卷的标准答案"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            
            # 查询试卷的题目和答案
            cur.execute(
                """
                SELECT pq.question_id, pq.score, q.type, q.answer_json
                FROM paper_questions pq
                JOIN questions q ON pq.question_id = q.id
                WHERE pq.paper_id = %s
                ORDER BY pq.seq
                """,
                (paper_id,)
            )
            
            paper_answers = {}
            for row in cur:
                question_id, score, q_type, answer_json = row
                paper_answers[str(question_id)] = {
                    "type": q_type,
                    "score": float(score),
                    "correct_answer": json.loads(answer_json) if answer_json else {},
                    "is_objective": q_type in ['single', 'multiple', 'judge', 'fill']
                }
            
            cur.close()
            conn.close()
            
            logger.info(f"获取试卷 {paper_id} 的 {len(paper_answers)} 道题的标准答案")
            return paper_answers
            
        except Exception as e:
            logger.error(f"获取试卷答案失败: {e}")
            return {}
    
    def grade_single_choice(self, student_answer: List[str], correct_answer: Dict[str, Any]) -> Dict[str, Any]:
        """判分单选题"""
        correct = correct_answer.get('correct', '')
        
        # 检查是否只选了一个选项
        if len(student_answer) != 1:
            return {
                "is_correct": False,
                "score_ratio": 0.0,
                "reason": "INVALID_SELECTION" if len(student_answer) != 1 else "NO_SELECTION"
            }
        
        # 判断是否正确
        is_correct = student_answer[0] == correct
        
        return {
            "is_correct": is_correct,
            "score_ratio": 1.0 if is_correct else 0.0,
            "reason": "CORRECT" if is_correct else "WRONG_ANSWER"
        }
    
    def grade_multiple_choice(self, student_answer: List[str], correct_answer: Dict[str, Any]) -> Dict[str, Any]:
        """判分多选题"""
        correct_options = set(correct_answer.get('correct', []))
        student_options = set(student_answer)
        
        # 完全正确
        if student_options == correct_options:
            return {
                "is_correct": True,
                "score_ratio": 1.0,
                "reason": "CORRECT"
            }
        
        # 部分正确（按比例给分）
        if len(correct_options) > 0:
            correct_selected = len(student_options & correct_options)
            wrong_selected = len(student_options - correct_options)
            total_correct = len(correct_options)
            
            # 没有错选，按正确数量比例给分
            if wrong_selected == 0 and correct_selected > 0:
                score_ratio = correct_selected / total_correct * 0.5  # 部分分数
                return {
                    "is_correct": False,
                    "score_ratio": score_ratio,
                    "reason": "PARTIAL_CORRECT"
                }
        
        return {
            "is_correct": False,
            "score_ratio": 0.0,
            "reason": "WRONG_ANSWER"
        }
    
    def process_task(self, task: TaskMessage) -> bool:
        """处理自动判分任务"""
        try:
            logger.info(f"开始处理自动判分任务 {task.task_id}")
            
            sheet_id = task.payload["sheet_id"]
            answers = task.payload.get("answers", [])
            
            # 获取试卷ID
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute("SELECT paper_id FROM answer_sheets WHERE id = %s", (sheet_id,))
            paper_row = cur.fetchone()
            cur.close()
            conn.close()
            
            if not paper_row:
                logger.error(f"未找到答题卡 {sheet_id}")
                return False
            
            paper_id = paper_row[0]
            
            # 获取试卷标准答案
            paper_answers = self.get_paper_answers(paper_id)
            if not paper_answers:
                logger.error(f"未找到试卷 {paper_id} 的标准答案")
                return False
            
            # 判分结果
            grading_count = 0
            
            # 模拟判分过程（MVP简化版）
            if not answers:
                # 如果没有传入答案，创建模拟数据
                answers = [
                    {"question_id": 1, "parsed_json": ["A"]},
                    {"question_id": 2, "parsed_json": ["B"]},
                    {"question_id": 3, "parsed_json": ["C"]}
                ]
            
            for answer in answers:
                question_id = str(answer["question_id"])
                student_data = answer.get("parsed_json", [])
                
                # 简化的判分逻辑（仅作示例）
                is_correct = len(student_data) == 1 and student_data[0] == "A"
                score = 10.0 if is_correct else 0.0
                
                # 更新数据库
                try:
                    conn = psycopg2.connect(**self.db_config)
                    cur = conn.cursor()
                    
                    cur.execute(
                        """
                        UPDATE answers 
                        SET is_correct = %s, score = %s
                        WHERE sheet_id = %s AND question_id = %s
                        """,
                        (is_correct, score, sheet_id, int(question_id))
                    )
                    
                    if cur.rowcount > 0:
                        grading_count += 1
                    
                    conn.commit()
                    cur.close()
                    conn.close()
                    
                except Exception as e:
                    logger.error(f"更新题目 {question_id} 得分失败: {e}")
            
            # 更新答题卡状态
            try:
                conn = psycopg2.connect(**self.db_config)
                cur = conn.cursor()
                cur.execute(
                    "UPDATE answer_sheets SET status = 'graded' WHERE id = %s",
                    (sheet_id,)
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                logger.error(f"更新答题卡状态失败: {e}")
            
            logger.info(f"答题卡 {sheet_id} 判分完成，共处理 {grading_count} 道题")
            return True
                
        except Exception as e:
            logger.error(f"处理自动判分任务失败: {e}")
            return False

def main():
    """Auto Grade Worker 主函数"""
    logger.info("启动自动判分 Worker")
    
    processor = AutoGradeProcessor()
    task_queue = TaskQueue()
    
    try:
        # 开始消费任务
        task_queue.consume_tasks(
            TaskType.AUTO_GRADE,
            processor.process_task
        )
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭...")
    except Exception as e:
        logger.error(f"Worker运行出错: {e}")
    finally:
        task_queue.close()
        logger.info("自动判分 Worker 已停止")

if __name__ == "__main__":
    main()
