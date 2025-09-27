#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版正则表达式文档处理器
结合多种策略提升识别率
"""

import re
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EnhancedRegexProcessor:
    """增强版正则表达式处理器"""
    
    def __init__(self):
        # 多种题号格式的正则表达式
        self.question_patterns = [
            # 标准数字题号
            (r'(?:^|\n)\s*([1-9]\d*)[.．]\s*([^\n]+(?:\n(?!\s*\d+[.．]|\s*[一二三四五六七八九十][、.]|\s*第\s*\d)[^\n]*)*)', 'number_dot'),
            (r'(?:^|\n)\s*([1-9]\d*)、\s*([^\n]+(?:\n(?!\s*\d+、|\s*[一二三四五六七八九十][、.])[^\n]*)*)', 'number_comma'),
            (r'(?:^|\n)\s*([1-9]\d*)\)\s*([^\n]+(?:\n(?!\s*\d+\)|\s*[一二三四五六七八九十][、.])[^\n]*)*)', 'number_paren'),
            (r'(?:^|\n)\s*\(([1-9]\d*)\)\s*([^\n]+(?:\n(?!\s*\(\d+\)|\s*[一二三四五六七八九十][、.])[^\n]*)*)', 'number_both_paren'),
            
            # 中文题号
            (r'(?:^|\n)\s*第\s*([一二三四五六七八九十]+)\s*题[：:]\s*([^\n]+(?:\n(?!\s*第\s*[一二三四五六七八九十]+\s*题)[^\n]*)*)', 'chinese_formal'),
            (r'(?:^|\n)\s*([一二三四五六七八九十]+)[、.]\s*([^\n]+(?:\n(?!\s*[一二三四五六七八九十]+[、.]|\s*\d+[.．])[^\n]*)*)', 'chinese_simple'),
            
            # 特殊格式
            (r'(?:^|\n)\s*题目\s*([1-9]\d*)[：:]\s*([^\n]+(?:\n(?!\s*题目\s*\d+[：:])[^\n]*)*)', 'formal_title'),
            (r'(?:^|\n)\s*Q([1-9]\d*)[.．]\s*([^\n]+(?:\n(?!\s*Q\d+[.．])[^\n]*)*)', 'q_format'),
        ]
        
        # 中文数字转换
        self.chinese_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20
        }
    
    def smart_split_text(self, text: str) -> List[Dict[str, Any]]:
        """智能拆分文档文本"""
        logger.info(f"开始增强版文本拆分，长度: {len(text)} 字符")
        
        # 预处理文本
        cleaned_text = self._preprocess_text(text)
        
        # 尝试多种模式匹配
        best_result = []
        best_score = 0
        
        for pattern, pattern_name in self.question_patterns:
            try:
                matches = re.findall(pattern, cleaned_text, re.MULTILINE | re.DOTALL)
                if matches:
                    questions = self._process_matches(matches, pattern_name)
                    score = self._evaluate_extraction_quality(questions)
                    
                    logger.info(f"模式 {pattern_name}: 找到 {len(questions)} 道题目，评分: {score:.2f}")
                    
                    if score > best_score:
                        best_result = questions
                        best_score = score
                        
            except Exception as e:
                logger.warning(f"模式 {pattern_name} 处理失败: {e}")
                continue
        
        # 如果正则表达式效果不好，使用备用策略
        if len(best_result) < 3 or best_score < 0.6:
            logger.info("正则表达式效果不佳，尝试备用策略")
            fallback_result = self._fallback_strategies(cleaned_text)
            if len(fallback_result) > len(best_result):
                best_result = fallback_result
        
        logger.info(f"最终识别 {len(best_result)} 道题目")
        return best_result
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 移除页眉页脚等干扰信息
        noise_patterns = [
            r'第\s*\d+\s*页\s*共\s*\d+\s*页',
            r'姓名[：:]\s*_+\s*学号[：:]\s*_+',
            r'考试时间[：:]\s*\d+\s*分钟',
            r'满分[：:]\s*\d+\s*分',
            r'注意事项[：:].*?(?=\n\s*\d+[.．]|$)',
            r'答题说明[：:].*?(?=\n\s*\d+[.．]|$)',
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # 清理多余空行
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        return text.strip()
    
    def _process_matches(self, matches: List[tuple], pattern_name: str) -> List[Dict[str, Any]]:
        """处理正则匹配结果"""
        questions = []
        
        for match in matches:
            if len(match) >= 2:
                num_str, content = match[0], match[1]
                
                # 转换题号
                if pattern_name.startswith('chinese'):
                    seq_num = self._chinese_to_number(num_str)
                else:
                    seq_num = int(num_str) if num_str.isdigit() else len(questions) + 1
                
                # 清理和格式化内容
                formatted_content = self._format_question_content(content.strip())
                
                # 验证题目有效性
                if self._is_valid_question_content(formatted_content):
                    question_item = self._create_question_item(formatted_content, seq_num)
                    questions.append(question_item)
        
        return questions
    
    def _chinese_to_number(self, chinese_num: str) -> int:
        """中文数字转阿拉伯数字"""
        return self.chinese_numbers.get(chinese_num, 1)
    
    def _format_question_content(self, content: str) -> str:
        """格式化题目内容"""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 格式化选择项
            if re.match(r'^[A-Z][.．]\s*', line):
                formatted_lines.append('    ' + line)
            # 格式化数学表达式
            elif any(symbol in line for symbol in ['=', '+', '-', '×', '÷', '∫', 'lim']):
                formatted_lines.append(self._format_math_expression(line))
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_math_expression(self, line: str) -> str:
        """格式化数学表达式"""
        # 标准化数学符号周围的空格
        line = re.sub(r'\s*=\s*', ' = ', line)
        line = re.sub(r'\s*\+\s*', ' + ', line)
        line = re.sub(r'\s*-\s*', ' - ', line)
        line = re.sub(r'\s*×\s*', ' × ', line)
        line = re.sub(r'\s*÷\s*', ' ÷ ', line)
        return line
    
    def _is_valid_question_content(self, content: str) -> bool:
        """验证题目内容有效性"""
        # 基本长度检查
        if len(content.strip()) < 10:
            return False
        
        # 检查是否包含题目特征
        question_indicators = [
            r'[?？]',  # 问号
            r'下列.*?是|哪.*?是|什么.*?是',  # 问题词
            r'计算|求|证明|分析|简述|论述',  # 题目动词
            r'正确.*?是|错误.*?是',  # 判断题
            r'[A-D][.．].*?[A-D][.．]',  # 选择题特征
            r'_{3,}',  # 填空题特征
            r'[（(]\s*[）)]\s*$',  # 判断题括号
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in question_indicators)
    
    def _create_question_item(self, content: str, seq: int) -> Dict[str, Any]:
        """创建题目项"""
        question_type = self._detect_question_type(content)
        confidence = self._calculate_confidence(content, question_type)
        
        return {
            'seq': seq,
            'question_text': content,
            'question_type': question_type,
            'confidence': confidence,
            'ocr_result': {
                'text': content,
                'type': question_type,
                'confidence': confidence
            },
            'candidate_kps': self._suggest_knowledge_points(content),
            'review_status': 'pending'
        }
    
    def _detect_question_type(self, text: str) -> str:
        """检测题目类型"""
        text_lower = text.lower()
        
        # 判断题
        if re.search(r'[（(]\s*[）)]\s*$', text) or '判断' in text:
            return 'judge'
        
        # 填空题
        if re.search(r'_{3,}|……|[（(]\s*[）)]', text):
            return 'fill'
        
        # 选择题
        choice_count = len(re.findall(r'[A-D][.．]', text))
        if choice_count >= 2:
            if '多选' in text or '哪些' in text:
                return 'multiple'
            return 'single'
        
        # 主观题
        subjective_patterns = [
            r'计算|求|证明|分析|简述|论述',
            r'为什么|怎么样|如何.*?理解',
            r'谈谈.*?看法|结合.*?说明',
        ]
        
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in subjective_patterns):
            return 'subjective'
        
        return 'single'  # 默认
    
    def _calculate_confidence(self, text: str, question_type: str) -> float:
        """计算置信度"""
        base_confidence = 0.7
        
        # 根据文本特征调整
        if len(text) < 20:
            base_confidence -= 0.3
        elif len(text) > 100:
            base_confidence += 0.2
        
        # 根据题型特征调整
        if question_type == 'single':
            choices = len(re.findall(r'[A-D][.．]', text))
            if choices >= 4:
                base_confidence += 0.2
        elif question_type == 'fill':
            blanks = len(re.findall(r'_{3,}', text))
            if blanks > 0:
                base_confidence += 0.1
        
        return min(1.0, max(0.1, base_confidence))
    
    def _suggest_knowledge_points(self, text: str) -> List[str]:
        """建议知识点"""
        # 简单的关键词匹配
        keywords_map = {
            '函数': ['函数基础', '函数性质'],
            '极限': ['极限运算', '极限理论'],
            '导数': ['导数计算', '导数应用'],
            '积分': ['不定积分', '定积分'],
            '复数': ['复数运算', '复数几何'],
            '方程': ['方程解法', '方程组'],
        }
        
        suggested_kps = []
        for keyword, kps in keywords_map.items():
            if keyword in text:
                suggested_kps.extend(kps)
        
        return suggested_kps[:3]  # 最多返回3个
    
    def _evaluate_extraction_quality(self, questions: List[Dict]) -> float:
        """评估提取质量"""
        if not questions:
            return 0.0
        
        score = 0.0
        
        # 题目数量得分
        count_score = min(1.0, len(questions) / 10.0)
        score += count_score * 0.3
        
        # 平均置信度得分
        avg_confidence = sum(q.get('confidence', 0) for q in questions) / len(questions)
        score += avg_confidence * 0.4
        
        # 内容质量得分
        avg_length = sum(len(q.get('question_text', '')) for q in questions) / len(questions)
        length_score = min(1.0, avg_length / 100.0)
        score += length_score * 0.3
        
        return score
    
    def _fallback_strategies(self, text: str) -> List[Dict[str, Any]]:
        """备用拆分策略"""
        questions = []
        
        # 策略1: 基于问号分割
        question_parts = re.split(r'[?？]\s*(?=\n|$)', text)
        for i, part in enumerate(question_parts[:-1]):
            part = part.strip()
            if len(part) > 20 and self._is_valid_question_content(part + '？'):
                questions.append(self._create_question_item(part + '？', i + 1))
        
        # 策略2: 基于段落分割
        if len(questions) < 3:
            paragraphs = re.split(r'\n\s*\n+', text)
            for i, para in enumerate(paragraphs):
                para = para.strip()
                if len(para) > 30 and self._is_valid_question_content(para):
                    questions.append(self._create_question_item(para, i + 1))
        
        return questions[:20]  # 最多返回20道题

def test_enhanced_processor():
    """测试增强处理器"""
    processor = EnhancedRegexProcessor()
    
    test_text = """
数学综合测试

1. 下列哪个函数是奇函数？
   A. f(x) = x² + 1
   B. f(x) = x³ - x
   C. f(x) = |x|
   D. f(x) = x² - 1

2. 计算极限 lim(x→0) (sin 3x)/(tan 2x) = ?
   A. 1
   B. 3/2
   C. 2/3
   D. 0

3. 若函数 f(x) = ax² + bx + c 在 x = 1 处取最小值 2，且 f(0) = 3，
   则 a = ______，b = ______。

4. 函数 f(x) = x² 在 R 上单调递增。（　　）

第五题：证明：在直角三角形ABC中，∠C = 90°，则有 a² + b² = c²。
"""
    
    result = processor.smart_split_text(test_text)
    
    print(f"增强处理器识别结果：{len(result)} 道题目")
    for i, item in enumerate(result, 1):
        print(f"\n题目 {i}:")
        print(f"类型: {item['question_type']}")
        print(f"置信度: {item['confidence']:.2f}")
        print(f"内容: {item['question_text'][:100]}...")

if __name__ == "__main__":
    test_enhanced_processor()