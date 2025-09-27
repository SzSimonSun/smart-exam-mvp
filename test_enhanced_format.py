#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强格式保持功能测试
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.real_document_processor import DocumentProcessor
import json

def create_test_document():
    """创建包含复杂格式的测试文档内容"""
    return """
《数学综合测试题》

一、单项选择题（每题5分，共30分）

1. 下列哪个函数是奇函数？
   A. f(x) = x² + 1
   B. f(x) = x³ - x
   C. f(x) = |x|
   D. f(x) = x² - 1

2. 已知集合 A = {x | x² - 3x + 2 = 0}，集合 B = {1, 2, 3}，则 A ∩ B = ？
   A. {1}
   B. {2}
   C. {1, 2}
   D. {1, 2, 3}

3. 计算极限 lim(x→0) (sin x)/x 的值是：
   A. 0
   B. 1
   C. ∞
   D. 不存在

二、填空题（每题8分，共24分）

4. 若函数 f(x) = ax² + bx + c 在点 x = 1 处取得最小值 2，且 f(0) = 3，则 a = ______，b = ______。

5. 在直角坐标系中，点 A(2, 3) 关于直线 y = x 的对称点坐标是 __________。

6. 设 z = 3 + 4i，则 |z| = ______，arg(z) = ______。

三、判断题（每题4分，共16分）

7. 任何两个向量都可以进行数量积运算。（　　）

8. 若函数 f(x) 在点 x₀ 处连续，则 f(x) 在 x₀ 处一定可导。（　　）

9. 对于任意实数 a、b，不等式 a² + b² ≥ 2ab 总是成立的。（　　）

10. 矩阵的行列式值为 0 当且仅当该矩阵不可逆。（　　）

四、计算题（每题15分，共30分）

11. 已知函数 f(x) = x³ - 3x² + 2x + 1
    (1) 求 f'(x)；
    (2) 求 f(x) 的极值点；
    (3) 画出 f(x) 的大致图像。

12. 解积分方程：
    ∫₀ˣ f(t)dt = x² + 2x - 1
    其中 f(x) 是连续函数。
    
    要求：
    (1) 求出 f(x) 的表达式；
    (2) 验证你的答案。
"""

def test_format_preservation():
    """测试格式保持功能"""
    print("=" * 80)
    print("增强格式保持功能测试")
    print("=" * 80)
    
    processor = DocumentProcessor()
    
    # 测试复杂格式文档
    test_content = create_test_document()
    
    print(f"\n原始文档内容长度: {len(test_content)} 字符")
    print(f"原始文档前500字符:\n{test_content[:500]}...")
    
    # 处理文档
    result = processor._smart_split_text(test_content)
    
    print(f"\n识别到 {len(result)} 道题目：")
    print("-" * 60)
    
    for i, item in enumerate(result, 1):
        question_type = item.get('question_type', 'unknown')
        confidence = item.get('confidence', 0.0)
        question_text = item.get('question_text', '')
        
        print(f"\n题目 {i} (类型: {question_type}):")
        print(f"置信度: {confidence:.2f}")
        print(f"内容:")
        print(question_text)
        print("-" * 40)
        
        # 分析格式保持情况
        lines = question_text.split('\n')
        indent_count = sum(1 for line in lines if line.startswith('  '))
        math_symbols = sum(question_text.count(sym) for sym in ['=', '+', '-', '×', '÷'])
        
        print(f"格式分析 - 缩进行数: {indent_count}, 数学符号: {math_symbols}")
        print("-" * 40)

def test_specific_formats():
    """测试特定格式处理"""
    print("\n" + "=" * 60)
    print("测试特定格式处理功能")
    print("=" * 60)
    
    processor = DocumentProcessor()
    
    # 测试数学公式格式保持
    math_text = """
1. 求解方程组：
   x + y = 5
   2x - y = 1
   
   A. x = 2, y = 3
   B. x = 3, y = 2  
   C. x = 1, y = 4
   D. x = 4, y = 1
"""
    
    print("数学公式格式测试:")
    formatted = processor._preserve_question_format(math_text.strip())
    print(repr(formatted))
    
    # 测试选择项对齐
    choice_text = """
下列哪个函数是偶函数？
A. f(x) = x² + 1
B. f(x) = x³ - x
C. f(x) = |x| + x
D. f(x) = sin(x)
"""
    
    print("\n选择项对齐测试:")
    formatted = processor._preserve_question_format(choice_text.strip())
    print(repr(formatted))

if __name__ == "__main__":
    test_format_preservation()
    test_specific_formats()