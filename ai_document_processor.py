#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI增强文档处理器
集成多种AI模型提升识别率
"""

import json
import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AIDocumentProcessor:
    """AI增强文档处理器"""
    
    def __init__(self):
        self.models = {
            'openai': None,  # OpenAI GPT-4
            'claude': None,  # Anthropic Claude
            'qwen': None,    # 阿里 Qwen
            'local': None,   # 本地模型
        }
        
        # 初始化可用的AI模型
        self._initialize_models()
    
    def _initialize_models(self):
        """初始化AI模型"""
        try:
            # 尝试导入和初始化各种模型
            self._try_init_openai()
            self._try_init_local_models()
        except Exception as e:
            logger.warning(f"AI模型初始化部分失败: {e}")
    
    def _try_init_openai(self):
        """尝试初始化OpenAI模型"""
        try:
            import openai
            # 需要配置API密钥
            self.models['openai'] = openai
            logger.info("OpenAI模型初始化成功")
        except ImportError:
            logger.info("OpenAI库未安装，跳过")
    
    def _try_init_local_models(self):
        """尝试初始化本地模型"""
        try:
            # 可以集成Transformers、Langchain等
            from transformers import pipeline
            
            # 使用中文语言模型
            self.models['local'] = {
                'ner': pipeline("ner", model="hfl/chinese-roberta-wwm-ext"),
                'classification': pipeline("text-classification", 
                                         model="hfl/chinese-roberta-wwm-ext")
            }
            logger.info("本地模型初始化成功")
        except ImportError:
            logger.info("Transformers库未安装，跳过本地模型")
    
    def analyze_document_with_ai(self, text: str, use_model: str = 'auto') -> List[Dict[str, Any]]:
        """使用AI分析文档"""
        if use_model == 'auto':
            use_model = self._select_best_available_model()
        
        if use_model == 'openai' and self.models['openai']:
            return self._analyze_with_openai(text)
        elif use_model == 'local' and self.models['local']:
            return self._analyze_with_local_model(text)
        else:
            # 回退到增强正则表达式
            from enhanced_regex_processor import EnhancedRegexProcessor
            processor = EnhancedRegexProcessor()
            return processor.smart_split_text(text)
    
    def _select_best_available_model(self) -> str:
        """选择最佳可用模型"""
        if self.models['openai']:
            return 'openai'
        elif self.models['local']:
            return 'local'
        else:
            return 'regex'
    
    def _analyze_with_openai(self, text: str) -> List[Dict[str, Any]]:
        """使用OpenAI分析文档"""
        try:
            client = self.models['openai'].OpenAI()
            
            prompt = self._build_analysis_prompt(text)
            
            response = client.chat.completions.create(
                model="gpt-4o",  # 或 gpt-4o-mini
                messages=[
                    {"role": "system", "content": "你是一个专业的试卷分析专家，擅长准确识别和拆分考试题目。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content
            return self._parse_ai_response(result_text)
            
        except Exception as e:
            logger.error(f"OpenAI分析失败: {e}")
            return []
    
    def _analyze_with_local_model(self, text: str) -> List[Dict[str, Any]]:
        """使用本地模型分析文档"""
        try:
            # 使用NER识别题目边界
            ner_results = self.models['local']['ner'](text)
            
            # 基于NER结果拆分题目
            questions = self._extract_questions_from_ner(text, ner_results)
            
            # 使用分类模型判断题目类型
            for question in questions:
                question_text = question['question_text']
                classification = self.models['local']['classification'](question_text)
                question['question_type'] = self._map_classification_to_type(classification)
                question['confidence'] = classification[0]['score']
            
            return questions
            
        except Exception as e:
            logger.error(f"本地模型分析失败: {e}")
            return []
    
    def _build_analysis_prompt(self, text: str) -> str:
        """构建AI分析提示词"""
        return f"""
请分析以下考试试卷文档，准确识别并拆分每道题目。

要求：
1. 识别每道题目的完整内容（包括题号、题干、选项、填空等）
2. 判断题目类型：single(单选)、multiple(多选)、fill(填空)、judge(判断)、subjective(主观)
3. 保持原有格式和排版
4. 给出识别置信度(0-1之间的小数)
5. 建议相关知识点

输出格式：
```json
[
    {{
        "seq": 1,
        "question_text": "完整的题目内容，保持原格式",
        "question_type": "single",
        "confidence": 0.95,
        "suggested_kps": ["相关知识点1", "相关知识点2"],
        "analysis": "简要分析说明"
    }},
    ...
]
```

文档内容：
{text[:3000]}  # 限制长度避免超出token限制
"""
    
    def _parse_ai_response(self, response_text: str) -> List[Dict[str, Any]]:
        """解析AI响应"""
        try:
            # 提取JSON部分
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                # 如果没有代码块，尝试直接解析
                json_text = response_text
            
            questions = json.loads(json_text)
            
            # 验证和标准化结果
            validated_questions = []
            for i, q in enumerate(questions):
                if self._validate_ai_question(q):
                    # 添加必要的字段
                    validated_q = {
                        'seq': q.get('seq', i + 1),
                        'question_text': q.get('question_text', ''),
                        'question_type': q.get('question_type', 'single'),
                        'confidence': q.get('confidence', 0.8),
                        'ocr_result': {
                            'text': q.get('question_text', ''),
                            'type': q.get('question_type', 'single'),
                            'confidence': q.get('confidence', 0.8)
                        },
                        'candidate_kps': q.get('suggested_kps', []),
                        'review_status': 'pending'
                    }
                    validated_questions.append(validated_q)
            
            return validated_questions
            
        except Exception as e:
            logger.error(f"解析AI响应失败: {e}")
            return []
    
    def _validate_ai_question(self, question: Dict) -> bool:
        """验证AI返回的题目"""
        required_fields = ['question_text', 'question_type']
        return all(field in question for field in required_fields) and \
               len(question.get('question_text', '').strip()) > 10
    
    def _extract_questions_from_ner(self, text: str, ner_results: List) -> List[Dict[str, Any]]:
        """从NER结果中提取题目"""
        # 这里是简化版实现，实际应该更复杂
        questions = []
        
        # 基于题号位置分割文本
        question_starts = []
        for entity in ner_results:
            if re.match(r'\d+[.．]', entity.get('word', '')):
                question_starts.append(entity.get('start', 0))
        
        # 分割题目
        for i, start in enumerate(question_starts):
            end = question_starts[i + 1] if i + 1 < len(question_starts) else len(text)
            question_text = text[start:end].strip()
            
            if len(question_text) > 20:
                questions.append({
                    'seq': i + 1,
                    'question_text': question_text,
                    'question_type': 'single',  # 需要进一步分类
                    'confidence': 0.7
                })
        
        return questions
    
    def _map_classification_to_type(self, classification: List[Dict]) -> str:
        """将分类结果映射到题目类型"""
        # 这里需要根据实际模型的分类标签进行映射
        label = classification[0]['label']
        
        type_mapping = {
            'QUESTION': 'single',
            'CHOICE': 'single',
            'FILL': 'fill',
            'JUDGE': 'judge',
            'ESSAY': 'subjective'
        }
        
        return type_mapping.get(label, 'single')

# 使用示例和测试函数
def test_ai_processor():
    """测试AI处理器"""
    processor = AIDocumentProcessor()
    
    test_text = """
高等数学期末考试

1. 求极限 lim(x→0) (sin x)/x 的值是？
   A. 0
   B. 1  
   C. ∞
   D. 不存在

2. 函数 f(x) = x² + 2x + 1 的导数 f'(x) = ______。

3. 对于任意实数 x，都有 sin²x + cos²x = 1。（ ）

4. 计算题：求函数 f(x) = x³ - 3x² + 2 的极值。
   要求写出详细的求解过程。
"""
    
    result = processor.analyze_document_with_ai(test_text)
    
    print(f"AI处理器识别结果：{len(result)} 道题目")
    for i, item in enumerate(result, 1):
        print(f"\n题目 {i}:")
        print(f"类型: {item.get('question_type', 'unknown')}")
        print(f"置信度: {item.get('confidence', 0):.2f}")
        print(f"内容: {item.get('question_text', '')[:100]}...")

if __name__ == "__main__":
    test_ai_processor()