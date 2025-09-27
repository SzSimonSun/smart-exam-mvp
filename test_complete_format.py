#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整的格式保持功能测试和演示
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.real_document_processor import DocumentProcessor
import json

def create_formatted_test_document():
    """创建包含各种复杂格式的测试文档"""
    return """
《2024年高等数学期末考试试卷》

考试说明：
1. 本试卷共四大题，满分100分，考试时间120分钟
2. 答题时请保持字迹工整，计算过程清楚

一、单项选择题（每题5分，共30分）

1. 下列函数中，哪个是奇函数？
   A. f(x) = x² + 1
   B. f(x) = x³ - x  
   C. f(x) = |x|
   D. f(x) = x² - 1

2. 设 f(x) = ln(x + √(1 + x²))，则 f'(x) = ?
   A. 1/√(1 + x²)
   B. √(1 + x²)
   C. x/√(1 + x²)
   D. 1/(1 + x²)

3. 计算极限 lim(x→0) (sin 3x)/(tan 2x) = ?
   A. 1
   B. 3/2
   C. 2/3
   D. 0

二、填空题（每题6分，共24分）

4. 若函数 f(x) = ax² + bx + c 在点 x = 1 处取得最小值 2，且 f(0) = 3，
   则 a = ______，b = ______。

5. 在直角坐标系中，点 A(2, 3) 关于直线 y = x 的对称点坐标是 __________。

6. 设复数 z = 3 + 4i，则 |z| = ______，arg(z) = ______。

7. 曲线 y = x³ - 3x² + 2x + 1 在点 (1, 1) 处的切线方程是 __________。

三、判断题（每题3分，共12分）

8. 任何两个向量都可以进行数量积运算。（　　）

9. 若函数 f(x) 在点 x₀ 处连续，则 f(x) 在 x₀ 处一定可导。（　　）

10. 对于任意实数 a、b，不等式 a² + b² ≥ 2ab 总是成立的。（　　）

11. 矩阵的行列式值为 0 当且仅当该矩阵不可逆。（　　）

四、计算题（每题17分，共34分）

12. 已知函数 f(x) = x³ - 3x² + 2x + 1
    (1) 求 f'(x)；
    (2) 求 f(x) 的极值点；
    (3) 画出 f(x) 的大致图像。

13. 计算二重积分：
    ∬ᴅ (x² + y²) dxdy
    其中 D 是由圆 x² + y² = 4 围成的区域。
    
    要求：
    (1) 选择合适的坐标系；
    (2) 写出积分区域；
    (3) 计算积分值。
"""

def test_complete_format_preservation():
    """测试完整的格式保持功能"""
    print("=" * 100)
    print("完整格式保持功能测试与演示")
    print("=" * 100)
    
    # 创建测试文档
    test_document = create_formatted_test_document()
    
    print("🔍 原始文档分析:")
    print(f"   文档总长度: {len(test_document)} 字符")
    print(f"   行数: {len(test_document.split(chr(10)))}")
    pattern = r'\\d+[.\uff0e]'
    print(f"   包含的题号格式: {len(re.findall(pattern, test_document))} 个")
    
    # 使用改进的文档处理器
    processor = DocumentProcessor()
    result = processor._smart_split_text(test_document)
    
    print(f"\n🎯 拆分结果: 识别到 {len(result)} 道题目")
    print("=" * 100)
    
    for i, item in enumerate(result, 1):
        question_type = item.get('question_type', 'unknown')
        confidence = item.get('confidence', 0.0)
        question_text = item.get('question_text', '')
        
        print(f"\n📝 题目 {i} - {get_type_emoji(question_type)} {get_type_name(question_type)}")
        print(f"   置信度: {confidence:.1%} {get_confidence_emoji(confidence)}")
        print(f"   文本长度: {len(question_text)} 字符")
        
        # 分析格式特征
        lines = question_text.split('\n')
        choice_lines = [line for line in lines if re.match(r'^\\s*[A-D][.．]', line)]
        blank_lines = [line for line in lines if '_' in line]
        math_lines = [line for line in lines if any(symbol in line for symbol in ['=', '+', '-', '×', '÷', '²', '³', '√'])]
        
        print(f"   格式特征:")
        print(f"     - 总行数: {len(lines)}")
        if choice_lines:
            print(f"     - 选择项: {len(choice_lines)} 个")
        if blank_lines:
            print(f"     - 填空处: {len(blank_lines)} 处")
        if math_lines:
            print(f"     - 数学表达式: {len(math_lines)} 行")
        
        print(f"   格式保持效果:")
        print("   " + "─" * 80)
        # 显示格式化后的内容，保持缩进
        formatted_lines = question_text.split('\n')
        for line_num, line in enumerate(formatted_lines[:10], 1):  # 只显示前10行
            print(f"   {line_num:2d}│ {repr(line)}")
        
        if len(formatted_lines) > 10:
            print(f"   ...│ (还有 {len(formatted_lines) - 10} 行)")
        
        print("   " + "─" * 80)
        
        # 显示实际渲染效果
        print(f"   实际渲染效果:")
        for line in question_text.split('\n')[:5]:  # 只显示前5行的渲染效果
            print(f"   │ {line}")
        if len(question_text.split('\n')) > 5:
            print(f"   │ ...")
        
        print()

def get_type_emoji(type_name):
    """获取题型对应的emoji"""
    emoji_map = {
        'single': '🔵',
        'multiple': '🟢', 
        'fill': '📝',
        'judge': '⚖️',
        'subjective': '📚'
    }
    return emoji_map.get(type_name, '❓')

def get_type_name(type_name):
    """获取题型名称"""
    name_map = {
        'single': '单选题',
        'multiple': '多选题',
        'fill': '填空题', 
        'judge': '判断题',
        'subjective': '主观题'
    }
    return name_map.get(type_name, '未知类型')

def get_confidence_emoji(confidence):
    """根据置信度返回emoji"""
    if confidence >= 0.8:
        return "🎯"
    elif confidence >= 0.6:
        return "👍"
    elif confidence >= 0.4:
        return "⚠️"
    else:
        return "❌"

def demonstrate_format_improvements():
    """演示格式改进的效果"""
    print("\n" + "=" * 100)
    print("格式改进效果对比演示")
    print("=" * 100)
    
    # 测试不同格式的题目
    test_cases = [
        {
            "name": "选择题对齐测试",
            "content": """1. 下列哪个函数是偶函数？
A. f(x) = x³
B. f(x) = x²
C. f(x) = x
D. f(x) = x + 1"""
        },
        {
            "name": "数学公式保持测试", 
            "content": """2. 计算积分：
∫₀¹ x² dx = ?
解：根据积分公式：
∫ xⁿ dx = xⁿ⁺¹/(n+1) + C
所以：∫₀¹ x² dx = [x³/3]₀¹ = 1/3"""
        },
        {
            "name": "填空题格式测试",
            "content": """3. 设复数 z = a + bi，则：
|z| = ______
arg(z) = ______
z* = ______"""
        }
    ]
    
    processor = DocumentProcessor()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 测试用例 {i}: {test_case['name']}")
        print("─" * 50)
        
        # 显示原始内容
        print("原始内容:")
        for line in test_case['content'].split('\n'):
            print(f"  {repr(line)}")
        
        # 处理后的内容
        formatted = processor._preserve_question_format(test_case['content'])
        print("\n格式化后:")
        for line in formatted.split('\n'):
            print(f"  {repr(line)}")
        
        print("\n渲染效果:")
        print(formatted)
        print()

if __name__ == "__main__":
    import re
    test_complete_format_preservation()
    demonstrate_format_improvements()