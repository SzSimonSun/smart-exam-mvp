#!/usr/bin/env python3
"""
测试改进后的文档处理器
"""

import sys
import os
sys.path.append('/Users/sunfei/smart-exam-mvp/backend')
sys.path.append('/Users/sunfei/smart-exam-mvp/backend/app')

try:
    from app.services.real_document_processor import DocumentProcessor
except ImportError:
    # 备用导入方式
    sys.path.append('/Users/sunfei/smart-exam-mvp/backend/app/services')
    from real_document_processor import DocumentProcessor

def test_document_processor():
    processor = DocumentProcessor()
    
    # 测试用例1：标准试卷格式
    test_text1 = """
一、选择题（每题2分，共20分）

1. 下列哪个数是质数？
A. 4  B. 6  C. 7  D. 9

2. 计算 2 + 3 × 4 的结果是多少？
A. 20  B. 14  C. 10  D. 12

3. 下列哪些是偶数？（多选）
A. 2  B. 3  C. 4  D. 5  E. 6

二、填空题（每题3分，共15分）

4. 一元二次方程 x² - 5x + 6 = 0 的解是 ______

5. 圆的面积公式是 S = ______

三、判断题（每题2分，共10分）

6. 判断：所有的矩形都是正方形。（  ）

7. 正确说法是：质数只有两个因数。（  ）

四、简答题（每题10分，共20分）

8. 请简述勾股定理的内容及其应用。

9. 分析二次函数 y = x² - 4x + 3 的性质。
    """
    
    print("=" * 50)
    print("测试改进后的文档处理器")
    print("=" * 50)
    
    result = processor._smart_split_text(test_text1)
    
    print(f"识别到 {len(result)} 道题目：\n")
    
    for i, question in enumerate(result, 1):
        print(f"题目 {i}:")
        print(f"  内容: {question['question_text'][:100]}{'...' if len(question['question_text']) > 100 else ''}")
        print(f"  类型: {question['question_type']}")
        print(f"  置信度: {question['confidence']:.2f}")
        print(f"  知识点: {question['candidate_kps']}")
        print()
    
    # 测试用例2：问题格式试卷
    test_text2 = """
1. 什么是质数？请举例说明。

2. 如何计算圆的面积？公式是什么？

3. 二次函数的基本形式是什么？它有哪些性质？

4. 请证明：直角三角形中，斜边的平方等于两直角边的平方和。
    """
    
    print("=" * 50)
    print("测试问题格式试卷")
    print("=" * 50)
    
    result2 = processor._smart_split_text(test_text2)
    
    print(f"识别到 {len(result2)} 道题目：\n")
    
    for i, question in enumerate(result2, 1):
        print(f"题目 {i}:")
        print(f"  内容: {question['question_text']}")
        print(f"  类型: {question['question_type']}")
        print(f"  置信度: {question['confidence']:.2f}")
        print()

if __name__ == "__main__":
    test_document_processor()