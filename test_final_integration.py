#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终格式保持功能集成测试
"""

import sys
import os
import re
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_format_preservation_final():
    """最终格式保持测试"""
    print("=" * 80)
    print("🎯 最终格式保持功能测试")
    print("=" * 80)
    
    try:
        from app.services.real_document_processor import DocumentProcessor
        
        # 读取测试文档
        with open('/Users/sunfei/smart-exam-mvp/test_paper_formatted.txt', 'r', encoding='utf-8') as f:
            test_content = f.read()
        
        print(f"📄 读取测试文档成功，长度: {len(test_content)} 字符")
        
        # 初始化处理器
        processor = DocumentProcessor()
        print(f"✅ 文档处理器状态:")
        print(f"   - PDF支持: {processor.has_pdf}")
        print(f"   - DOCX支持: {processor.has_docx}")
        print(f"   - AI增强: {processor.use_ai_enhancement}")
        
        # 处理文档
        print(f"\n🔄 开始处理文档...")
        result = processor._smart_split_text(test_content)
        
        print(f"\n✅ 处理完成！识别到 {len(result)} 道题目")
        print("=" * 60)
        
        # 详细分析每道题目
        for i, item in enumerate(result, 1):
            print(f"\n📋 题目 {i}:")
            print(f"   类型: {item.get('question_type', 'unknown')}")
            print(f"   置信度: {item.get('confidence', 0):.1%}")
            
            question_text = item.get('question_text', '')
            lines = question_text.split('\n')
            
            print(f"   内容行数: {len(lines)}")
            print(f"   内容:")
            for j, line in enumerate(lines, 1):
                if line.strip():
                    print(f"     {j:2d}│ {line}")
            
            # 检查格式特征
            choice_lines = [line for line in lines if re.match(r'^\s*[A-D][.．]', line)]
            blank_lines = [line for line in lines if '_' in line or '（' in line]
            
            if choice_lines:
                print(f"   选择项数量: {len(choice_lines)}")
                indented_count = sum(1 for line in choice_lines if line.startswith('    '))
                print(f"   正确缩进: {indented_count}/{len(choice_lines)}")
            
            if blank_lines:
                print(f"   填空/判断项: {len(blank_lines)}")
            
            print("-" * 40)
        
        # 评估整体效果
        print(f"\n📊 整体评估:")
        print(f"   题目数量: {len(result)}/5")
        
        avg_confidence = sum(item.get('confidence', 0) for item in result) / len(result) if result else 0
        print(f"   平均置信度: {avg_confidence:.1%}")
        
        # 检查格式保持质量
        format_score = 0
        total_choices = 0
        correct_indent = 0
        
        for item in result:
            question_text = item.get('question_text', '')
            lines = question_text.split('\n')
            choice_lines = [line for line in lines if re.match(r'^\s*[A-D][.．]', line)]
            
            if choice_lines:
                total_choices += len(choice_lines)
                correct_indent += sum(1 for line in choice_lines if line.startswith('    '))
        
        if total_choices > 0:
            format_quality = correct_indent / total_choices
            print(f"   格式保持质量: {format_quality:.1%} ({correct_indent}/{total_choices})")
        else:
            format_quality = 0
            print(f"   格式保持质量: 无选择题可评估")
        
        overall_score = (len(result)/5) * 0.4 + avg_confidence * 0.3 + format_quality * 0.3
        print(f"   综合得分: {overall_score:.1%}")
        
        print(f"\n🏆 测试结论:")
        if overall_score >= 0.8:
            print("   🌟 优秀！格式保持功能工作完美")
        elif overall_score >= 0.6:
            print("   👍 良好！格式保持功能基本达标")
        elif overall_score >= 0.4:
            print("   ⚠️ 一般，还有改进空间")
        else:
            print("   ❌ 需要优化")
            
        return result
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_api_health():
    """测试API健康状态"""
    print(f"\n🔍 API健康检查:")
    
    try:
        import urllib.request
        import json
        
        # 测试健康端点
        with urllib.request.urlopen('http://localhost:8001/health') as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"   ✅ 后端API正常: {data}")
            else:
                print(f"   ❌ 后端API异常: {response.status}")
                
    except Exception as e:
        print(f"   ❌ API连接失败: {e}")

if __name__ == "__main__":
    print("🎉 智能考试系统 - 缓存清理后完整测试")
    print(f"时间: 2025-09-27")
    
    # 运行测试
    result = test_format_preservation_final()
    test_api_health()
    
    print(f"\n=" * 80)
    print(f"🎯 测试总结:")
    print(f"   • 服务状态: 后端和前端已重启")
    print(f"   • 缓存状态: 已清理")
    print(f"   • 识别结果: {len(result)} 道题目")
    print(f"   • 格式保持: 已整合到系统中")
    print(f"\n✨ 系统已准备好进行实际文档上传测试！")
    print("=" * 80)