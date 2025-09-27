"""
简化的文档处理服务
处理PDF、DOCX、图片文件，将试卷拆分为单个题目
"""

import json
import logging
import uuid
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """文档处理器（简化版本）"""
    
    def __init__(self):
        self.supported_types = {
            'application/pdf': self._process_pdf,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._process_docx,
            'image/jpeg': self._process_image,
            'image/jpg': self._process_image,
            'image/png': self._process_image,
        }
    
    def process_document(self, file_content: bytes, content_type: str, filename: str) -> Dict[str, Any]:
        """
        处理文档，拆分为题目
        
        Args:
            file_content: 文件内容
            content_type: 文件类型
            filename: 文件名
            
        Returns:
            处理结果，包含拆题项目列表
        """
        if content_type not in self.supported_types:
            return {
                'success': False,
                'error': f"不支持的文件类型: {content_type}",
                'items': []
            }
        
        try:
            processor = self.supported_types[content_type]
            result = processor(file_content, filename)
            
            # 为每个题目添加元数据
            for i, item in enumerate(result['items']):
                item['seq'] = i + 1
                item['id'] = str(uuid.uuid4())
                item['source_file'] = filename
                
            return result
            
        except Exception as e:
            logger.error(f"处理文档失败 {filename}: {e}")
            return {
                'success': False,
                'error': str(e),
                'items': []
            }
    
    def _process_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """处理PDF文件（简化版本）"""
        try:
            # 简化实现：直接使用模拟数据
            mock_text = f"""
1. 下列哪个数是质数？
A. 4  B. 6  C. 7  D. 9

2. 一元二次方程 x² - 5x + 6 = 0 的解是 ______

3. 判断：所有的矩形都是正方形。（  ）

4. 请简述三角形全等的判定方法。

（注：这是从 PDF {filename} 模拟识别的内容）
            """.strip()
            
            questions = self._split_text_into_questions(mock_text)
            
            return {
                'success': True,
                'file_type': 'pdf',
                'total_pages': 1,
                'items': questions,
                'message': f'从 PDF 中提取了 {len(questions)} 道题目'
            }
            
        except Exception as e:
            logger.error(f"PDF处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'items': []
            }
    
    def _process_docx(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """处理DOCX文件（简化版本）"""
        try:
            # 简化实现：直接使用模拟数据
            mock_text = f"""
1. 下列哪些是质数？（多选）
A. 2  B. 4  C. 7  D. 9  E. 11

2. 填空：一元二次方程 x² + 2x - 3 = 0 的解是 x = ______

3. 论述题：请讨论二次函数的性质及其在实际生活中的应用。

（注：这是从 DOCX {filename} 模拟识别的内容）
            """.strip()
            
            questions = self._split_text_into_questions(mock_text)
            
            return {
                'success': True,
                'file_type': 'docx',
                'total_paragraphs': 3,
                'items': questions,
                'message': f'从 DOCX 中提取了 {len(questions)} 道题目'
            }
            
        except Exception as e:
            logger.error(f"DOCX处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'items': []
            }
    
    def _process_image(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """处理图片文件（简化版本）"""
        try:
            # 简化实现：直接使用模拟数据
            mock_text = f"""
1. 下列哪个数是偶数？
A. 1  B. 3  C. 6  D. 7

2. 计算：3 × 4 + 2 = ______

3. 判断：正方形的四条边都相等。（  ）

（注：这是从图片 {filename} 模拟识别的内容）
            """.strip()
            
            questions = self._split_text_into_questions(mock_text)
            
            return {
                'success': True,
                'file_type': 'image',
                'image_size': (800, 600),
                'image_format': 'JPEG',
                'items': questions,
                'message': f'从图片中识别了 {len(questions)} 道题目'
            }
            
        except Exception as e:
            logger.error(f"图片处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'items': []
            }
    
    def _split_text_into_questions(self, text: str) -> List[Dict[str, Any]]:
        """将文本拆分为题目列表"""
        questions = []
        
        # 按数字题号分割（如 1. 2. 3. 或 1、2、3、）
        lines = text.split('\n')
        current_question = []
        question_pattern = re.compile(r'^\s*(\d+)[.、]\s*(.+)')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            match = question_pattern.match(line)
            if match:
                # 保存前一个题目
                if current_question:
                    question_text = '\n'.join(current_question)
                    if question_text.strip():
                        questions.append(self._create_question_item(question_text, len(questions) + 1))
                
                # 开始新题目
                current_question = [match.group(2)]
            else:
                if current_question:
                    current_question.append(line)
        
        # 保存最后一个题目
        if current_question:
            question_text = '\n'.join(current_question)
            if question_text.strip():
                questions.append(self._create_question_item(question_text, len(questions) + 1))
        
        # 如果没有识别到题号格式，尝试其他分割方式
        if not questions:
            questions = self._fallback_question_split(text)
        
        return questions
    
    def _create_question_item(self, question_text: str, seq: int) -> Dict[str, Any]:
        """创建拆题项目"""
        # 简单的题型识别
        question_type = self._detect_question_type(question_text)
        confidence = self._calculate_confidence(question_text, question_type)
        
        # 提取选项（如果是选择题）
        options = self._extract_options(question_text) if question_type in ['single', 'multiple'] else []
        
        return {
            'question_text': question_text.strip(),
            'question_type': question_type,
            'options': options,
            'confidence': confidence,
            'ocr_result': {
                'text': question_text.strip(),
                'type': question_type,
                'confidence': confidence
            },
            'candidate_kps': self._suggest_knowledge_points(question_text),
            'crop_uri': None,  # 图片裁剪URI，这里暂不实现
            'review_status': 'pending'
        }
    
    def _detect_question_type(self, text: str) -> str:
        """检测题目类型"""
        text_lower = text.lower()
        
        # 判断题关键词
        if any(keyword in text_lower for keyword in ['对错', '正确', '错误', '判断', '是否']):
            return 'judge'
        
        # 填空题关键词
        if '______' in text or '___' in text or '()' in text or '（）' in text:
            return 'fill'
        
        # 选择题关键词 - 多选
        if any(keyword in text_lower for keyword in ['多选', '多个', '下列哪些']):
            return 'multiple'
        
        # 选择题关键词 - 单选
        if any(keyword in text for keyword in ['A.', 'B.', 'C.', 'D.', 'A、', 'B、', 'C、', 'D、']):
            return 'single'
        
        # 主观题关键词
        if any(keyword in text_lower for keyword in ['论述', '分析', '说明', '解释', '简答', '计算']):
            return 'subjective'
        
        # 默认为单选题
        return 'single'
    
    def _extract_options(self, text: str) -> List[str]:
        """提取选择题选项"""
        options = []
        
        # 提取 A. B. C. D. 格式的选项
        option_pattern = re.compile(r'([A-Z])[.、]\s*([^\n]+)')
        matches = option_pattern.findall(text)
        
        for letter, content in matches:
            options.append(f"{letter}. {content.strip()}")
        
        return options
    
    def _calculate_confidence(self, text: str, question_type: str) -> float:
        """计算识别置信度"""
        base_confidence = 0.7
        
        # 根据文本长度调整
        if len(text) < 10:
            base_confidence -= 0.2
        elif len(text) > 100:
            base_confidence += 0.1
        
        # 根据题型特征调整
        if question_type == 'single' and ('A.' in text and 'B.' in text):
            base_confidence += 0.2
        elif question_type == 'fill' and ('___' in text or '（）' in text):
            base_confidence += 0.2
        
        return min(1.0, max(0.1, base_confidence))
    
    def _suggest_knowledge_points(self, text: str) -> List[Dict[str, Any]]:
        """建议知识点（简化实现）"""
        knowledge_suggestions = []
        
        # 数学关键词
        math_keywords = {
            '方程': {'subject': '数学', 'module': '代数', 'point': '方程', 'confidence': 0.8},
            '函数': {'subject': '数学', 'module': '代数', 'point': '函数', 'confidence': 0.8},
            '三角形': {'subject': '数学', 'module': '几何', 'point': '三角形', 'confidence': 0.9},
            '圆': {'subject': '数学', 'module': '几何', 'point': '圆', 'confidence': 0.8},
            '质数': {'subject': '数学', 'module': '数论', 'point': '质数', 'confidence': 0.9},
        }
        
        # 语文关键词
        chinese_keywords = {
            '阅读': {'subject': '语文', 'module': '阅读理解', 'point': '现代文', 'confidence': 0.7},
            '作文': {'subject': '语文', 'module': '写作', 'point': '记叙文', 'confidence': 0.7},
            '古诗': {'subject': '语文', 'module': '古代文学', 'point': '诗歌', 'confidence': 0.8},
        }
        
        # 英语关键词
        english_keywords = {
            'tense': {'subject': '英语', 'module': '语法', 'point': '时态', 'confidence': 0.8},
            'vocabulary': {'subject': '英语', 'module': '词汇', 'point': 'vocabulary', 'confidence': 0.7},
        }
        
        all_keywords = {**math_keywords, **chinese_keywords, **english_keywords}
        
        text_lower = text.lower()
        for keyword, kp_info in all_keywords.items():
            if keyword in text_lower:
                knowledge_suggestions.append(kp_info)
        
        # 如果没有匹配到，给个默认的
        if not knowledge_suggestions:
            knowledge_suggestions.append({
                'subject': '通用',
                'module': '基础',
                'point': '综合',
                'confidence': 0.5
            })
        
        return knowledge_suggestions
    
    def _fallback_question_split(self, text: str) -> List[Dict[str, Any]]:
        """备用的题目拆分逻辑"""
        # 如果无法按题号拆分，尝试按段落或其他规则拆分
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        questions = []
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 20:  # 过滤太短的段落
                questions.append(self._create_question_item(paragraph, i + 1))
        
        # 如果段落拆分也没有结果，至少创建一个题目
        if not questions and text.strip():
            questions.append(self._create_question_item(text.strip(), 1))
        
        return questions