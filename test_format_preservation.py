#!/usr/bin/env python3
"""
测试格式保持功能
"""

import sys
sys.path.append('/Users/sunfei/smart-exam-mvp/backend')

try:
    from app.services.real_document_processor import DocumentProcessor
except ImportError:
    sys.path.append('/Users/sunfei/smart-exam-mvp/backend/app/services')
    from real_document_processor import DocumentProcessor

def test_format_preservation():
    processor = DocumentProcessor()
    
    # 测试用例：包含复杂格式的试卷
    test_text = """
一、选择题（每题2分，共20分）

1. 下列哪个是质数？
   A. 4
   B. 6  
   C. 7
   D. 9

2. 计算 2x² + 3x - 1 = 0 的解：
   A. x = 1/2, x = -1
   B. x = -1/2, x = 1  
   C. x = 2, x = -1/2
   D. x = -2, x = 1/2

二、填空题（每题3分，共15分）

3. 一元二次方程 ax² + bx + c = 0（a ≠ 0）的求根公式是：
   x = _______________

4. 圆的面积公式：S = _______，其中 r 是半径。

三、解答题（每题10分，共30分）

5. 已知函数 f(x) = x² - 4x + 3
   (1) 求函数的对称轴
   (2) 求函数的最小值
   (3) 画出函数图像的大致形状

6. 证明题：证明在直角三角形ABC中，∠C = 90°，则有：
   a² + b² = c²
   其中c是斜边，a、b是直角边。
    """
    
    print("=" * 60)
    print("测试格式保持功能")
    print("=" * 60)
    
    result = processor._smart_split_text(test_text)
    
    print(f"识别到 {len(result)} 道题目：\n")
    
    for i, question in enumerate(result, 1):
        print(f"题目 {i} (序号: {question.get('seq', i)}):")
        print(f"类型: {question['question_type']}")
        print(f"置信度: {question['confidence']:.2f}")
        print("内容:")
        print(question['question_text'])
        print("-" * 50)

if __name__ == "__main__":
    test_format_preservation()