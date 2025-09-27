#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试前端格式保持功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.real_document_processor import DocumentProcessor
import json

def test_upload_and_verify_format():
    """测试上传文件并验证格式保持"""
    print("=" * 80)
    print("测试前端格式保持功能")
    print("=" * 80)
    
    # 创建一个包含多种格式的测试文档
    test_content = """
数学测试题

1. 计算下列积分：
   ∫₀¹ x² dx = ?
   
   A. 1/3
   B. 1/2  
   C. 2/3
   D. 1

2. 求解方程组：
   x + y = 5
   2x - y = 1
   
   A. x = 2, y = 3
   B. x = 3, y = 2
   C. x = 1, y = 4
   D. x = 4, y = 1

3. 判断题：函数 f(x) = x² 在 R 上单调递增。（　　）

4. 填空题：如果 a = 3，b = 4，则 √(a² + b²) = ______。

5. 简答题：请解释数学归纳法的基本原理，并举例说明其应用。
   要求：
   (1) 说明数学归纳法的两个步骤
   (2) 给出一个具体的证明例子
   (3) 分析该方法的优势和局限性
"""

    # 使用文档处理器处理
    processor = DocumentProcessor()
    result = processor._smart_split_text(test_content.strip())
    
    print(f"识别到 {len(result)} 道题目：")
    print("-" * 80)
    
    for i, item in enumerate(result, 1):
        question_type = item.get('question_type', 'unknown')
        confidence = item.get('confidence', 0.0)
        question_text = item.get('question_text', '')
        
        print(f"\n=== 题目 {i} ===")
        print(f"类型: {question_type}")
        print(f"置信度: {confidence:.2f}")
        print(f"格式化内容:")
        print(repr(question_text))  # 使用 repr 显示换行和缩进
        print(f"\n渲染效果:")
        print(question_text)
        print("-" * 60)
        
        # 分析格式特征
        lines = question_text.split('\n')
        print(f"行数: {len(lines)}")
        choice_lines = [line for line in lines if re.match(r'^\s*[A-D]\.', line)]
        print(f"选择项行数: {len(choice_lines)}")
        if choice_lines:
            print(f"选择项示例: {repr(choice_lines[0])}")
        print("=" * 60)

def test_api_format_preservation():
    """测试 API 格式保持"""
    print("\n" + "=" * 80)
    print("测试 API 格式保持")
    print("=" * 80)
    print("这部分需要后端服务运行，跳过...")

if __name__ == "__main__":
    import re
    test_upload_and_verify_format()
    test_api_format_preservation()