#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版格式保持功能集成测试
不依赖外部网络库
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_integrated_format_processing():
    """测试集成后的格式处理功能"""
    print("=" * 80)
    print("🧪 格式保持功能集成测试")
    print("=" * 80)
    
    try:
        from app.services.real_document_processor import DocumentProcessor
        
        # 创建测试文档
        test_document = """
数学综合测试题

1. 下列哪个函数是奇函数？
   A. f(x) = x² + 1
   B. f(x) = x³ - x
   C. f(x) = |x|
   D. f(x) = x² - 1

2. 计算极限值：
   lim(x→0) (sin 3x)/(tan 2x) = ?
   
   A. 1
   B. 3/2
   C. 2/3
   D. 0

3. 填空题：若 f(x) = ax² + bx + c 在 x = 1 处取最小值 2，且 f(0) = 3，
   则 a = ______，b = ______。

4. 判断题：函数 f(x) = x² 在 R 上单调递增。（　　）

5. 计算题：已知函数 f(x) = x³ - 3x² + 2x + 1
   (1) 求 f'(x)；
   (2) 求 f(x) 的极值点；
   (3) 画出 f(x) 的大致图像。
"""
        
        print("📄 测试文档内容已准备完成")
        print(f"文档长度: {len(test_document)} 字符")
        
        # 初始化文档处理器
        processor = DocumentProcessor()
        print(f"✅ 文档处理器初始化成功")
        print(f"   - PDF支持: {processor.has_pdf}")
        print(f"   - DOCX支持: {processor.has_docx}")
        print(f"   - AI增强: {processor.use_ai_enhancement}")
        
        # 处理文档
        print("\n🔄 开始处理文档...")
        result = processor._smart_split_text(test_document)
        
        print(f"\n✅ 文档处理完成！识别到 {len(result)} 道题目")
        print("=" * 60)
        
        # 详细展示每道题目
        for i, item in enumerate(result, 1):
            question_type = item.get('question_type', 'unknown')
            confidence = item.get('confidence', 0.0)
            question_text = item.get('question_text', '')
            
            print(f"\n📝 题目 {i} - {get_type_emoji(question_type)} {get_type_name(question_type)}")
            print(f"   置信度: {confidence:.1%} {get_confidence_emoji(confidence)}")
            
            # 分析格式特征
            lines = question_text.split('\n')
            choice_lines = [line for line in lines if re.match(r'^\s*[A-D][.．]', line)]
            blank_lines = [line for line in lines if '_' in line]
            math_lines = [line for line in lines if any(symbol in line for symbol in ['=', '+', '-', '×', '÷', '²', '³', '√', 'lim'])]
            
            print(f"   格式特征:")
            print(f"     - 总行数: {len(lines)}")
            if choice_lines:
                print(f"     - 选择项: {len(choice_lines)} 个")
                # 检查缩进效果
                proper_indent = sum(1 for line in choice_lines if line.startswith('    '))
                print(f"     - 正确缩进: {proper_indent}/{len(choice_lines)} 个")
            if blank_lines:
                print(f"     - 填空处: {len(blank_lines)} 处")
            if math_lines:
                print(f"     - 数学表达式: {len(math_lines)} 行")
            
            print(f"   📋 格式化内容示例:")
            # 显示前几行，展示格式效果
            for line_num, line in enumerate(lines[:6], 1):
                if line.strip():
                    # 显示缩进效果
                    indent_spaces = len(line) - len(line.lstrip())
                    indent_indicator = "→" * (indent_spaces // 4) if indent_spaces > 0 else ""
                    print(f"     {line_num:2d}│{indent_indicator}{line.strip()}")
            
            if len(lines) > 6:
                print(f"     ...│(省略 {len(lines) - 6} 行)")
            
            print("-" * 40)
        
        # 评估整合效果
        print(f"\n📊 整合效果评估:")
        total_questions = len(result)
        avg_confidence = sum(q.get('confidence', 0) for q in result) / total_questions if total_questions > 0 else 0
        
        # 检查格式保持效果
        format_quality = 0
        for item in result:
            question_text = item.get('question_text', '')
            lines = question_text.split('\n')
            
            # 检查选择项缩进
            choice_lines = [line for line in lines if re.match(r'^\s*[A-D][.．]', line)]
            if choice_lines:
                proper_indent_count = sum(1 for line in choice_lines if line.startswith('    '))
                format_quality += proper_indent_count / len(choice_lines) / total_questions
        
        print(f"   📈 题目识别率: {total_questions}/5 = {total_questions/5:.1%}")
        print(f"   📈 平均置信度: {avg_confidence:.1%}")
        print(f"   📈 格式保持质量: {format_quality:.1%}")
        
        overall_score = (total_questions/5) * 0.4 + avg_confidence * 0.3 + format_quality * 0.3
        print(f"   🎯 综合评分: {overall_score:.1%}")
        
        # 测试结果判定
        print(f"\n🏆 测试结果:")
        if overall_score >= 0.85:
            print("   🌟 优秀！格式保持功能完美集成")
        elif overall_score >= 0.7:
            print("   👍 良好！格式保持功能成功集成")
        elif overall_score >= 0.5:
            print("   ⚠️  一般，格式保持功能基本可用，建议优化")
        else:
            print("   ❌ 需要改进，格式保持功能集成效果不理想")
            
        return result
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保后端服务代码路径正确")
        return []
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []

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

def test_database_schema():
    """测试数据库结构"""
    print("\n" + "=" * 80)
    print("🗄️  数据库结构测试")
    print("=" * 80)
    
    try:
        # 检查迁移脚本
        migration_file = "/Users/sunfei/smart-exam-mvp/migrations/add_question_text_field.sql"
        if os.path.exists(migration_file):
            print("✅ 数据库迁移脚本已创建")
            with open(migration_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'question_text' in content:
                    print("✅ question_text字段迁移脚本正常")
                else:
                    print("⚠️ 迁移脚本可能有问题")
        else:
            print("❌ 数据库迁移脚本不存在")
            
        # 检查环境配置文件
        env_file = "/Users/sunfei/smart-exam-mvp/.env.example"
        if os.path.exists(env_file):
            print("✅ 环境配置文件已创建")
        else:
            print("❌ 环境配置文件不存在")
            
    except Exception as e:
        print(f"❌ 数据库结构测试失败: {e}")

def show_integration_summary():
    """显示整合总结"""
    print("\n" + "=" * 80)
    print("📋 格式保持功能整合总结")
    print("=" * 80)
    
    print("\n✅ 已完成的整合内容:")
    print("   1. 📝 后端文档处理器增强（格式保持 + AI支持）")
    print("   2. 🗄️  数据库schema升级（新增question_text字段）")
    print("   3. 🔌 API接口升级（支持格式化文本存储和返回）")
    print("   4. 🎨 前端显示优化（<pre>标签保持格式）")
    print("   5. ⚙️  配置文件和迁移脚本")
    
    print("\n🚀 整合特性:")
    print("   • 选择项自动缩进对齐（4个空格）")
    print("   • 数学公式符号格式化")  
    print("   • 填空题下划线标准化")
    print("   • 段落结构和换行保持")
    print("   • AI增强识别（可选）")
    print("   • 向后兼容现有数据")
    
    print("\n📋 下一步操作:")
    print("   1. 运行数据库迁移:")
    print("      sqlite3 smart_exam.db < migrations/add_question_text_field.sql")
    print("   2. 配置环境变量:")
    print("      cp .env.example .env")
    print("   3. 启动服务测试:")
    print("      cd backend && python -m uvicorn app.main:app --reload")
    print("   4. 上传测试文档验证格式保持效果")

if __name__ == "__main__":
    import re  # 需要导入re模块
    
    print("🎯 智能考试系统 - 格式保持功能集成测试")
    print("版本: 1.0.0")
    print("时间:", "2025-09-27")
    
    # 运行测试
    result = test_integrated_format_processing()
    test_database_schema()
    show_integration_summary()
    
    print(f"\n🎉 测试完成！共处理 {len(result)} 道题目")
    print("=" * 80)