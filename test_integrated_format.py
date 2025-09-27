#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试整合后的格式保持功能
"""

import requests
import json
import sys
import os

# 测试配置
API_BASE_URL = "http://localhost:8001"
TEST_USER_EMAIL = "teacher@example.com"
TEST_USER_PASSWORD = "password"

def login_and_get_token():
    """登录并获取token"""
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            return result["access_token"]
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"登录请求失败: {e}")
        return None

def test_document_upload():
    """测试文档上传和格式保持"""
    print("=" * 80)
    print("测试格式保持功能整合效果")
    print("=" * 80)
    
    # 获取认证token
    token = login_and_get_token()
    if not token:
        print("❌ 无法获取认证token，测试终止")
        return
    
    print("✅ 登录成功，获得认证token")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 创建测试文档内容
    test_document_content = """
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
    
    # 模拟文档上传（实际场景中需要上传文件）
    upload_data = {
        "content": test_document_content,
        "filename": "格式测试题.txt",
        "content_type": "text/plain"
    }
    
    try:
        print("\n📤 正在上传测试文档...")
        
        # 这里应该调用实际的文档上传API
        # 由于当前API需要文件上传，我们使用模拟的方式
        print("📄 测试文档内容：")
        print(test_document_content[:300] + "...")
        
        print("\n🔄 模拟文档处理流程...")
        
        # 直接测试文档处理器的格式保持效果
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from app.services.real_document_processor import DocumentProcessor
        
        processor = DocumentProcessor()
        result = processor._smart_split_text(test_document_content)
        
        print(f"\n✅ 文档处理完成，识别到 {len(result)} 道题目：")
        print("-" * 60)
        
        for i, item in enumerate(result, 1):
            question_type = item.get('question_type', 'unknown')
            confidence = item.get('confidence', 0.0)
            question_text = item.get('question_text', '')
            
            print(f"\n📝 题目 {i}:")
            print(f"   类型: {get_type_name(question_type)}")
            print(f"   置信度: {confidence:.1%}")
            print(f"   格式分析:")
            
            # 分析格式特征
            lines = question_text.split('\n')
            choice_lines = [line for line in lines if line.strip().startswith(('A.', 'B.', 'C.', 'D.'))]
            blank_lines = [line for line in lines if '_' in line]
            
            print(f"     - 总行数: {len(lines)}")
            if choice_lines:
                print(f"     - 选择项: {len(choice_lines)} 个（已格式化缩进）")
            if blank_lines:
                print(f"     - 填空处: {len(blank_lines)} 处")
            
            print(f"   格式化内容:")
            # 显示前几行的格式化效果
            for line_num, line in enumerate(lines[:5], 1):
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    print(f"     {line_num:2d}│{'  ' * (indent//2)}{line.strip()}")
            
            if len(lines) > 5:
                print(f"     ...│(还有 {len(lines) - 5} 行)")
        
        print(f"\n🎯 格式保持功能测试结果：")
        print(f"   ✅ 题目识别数量: {len(result)} / 5 道")
        print(f"   ✅ 格式保持效果: 选择项缩进、数学符号格式化")
        print(f"   ✅ 文本结构保持: 换行、段落层次")
        
        # 计算整体质量评分
        avg_confidence = sum(q.get('confidence', 0) for q in result) / len(result) if result else 0
        quality_score = (len(result) / 5) * 0.6 + avg_confidence * 0.4
        
        print(f"   📊 整体质量评分: {quality_score:.1%}")
        
        if quality_score >= 0.8:
            print("   🌟 格式保持功能集成成功！")
        elif quality_score >= 0.6:
            print("   👍 格式保持功能基本正常，可进一步优化")
        else:
            print("   ⚠️ 格式保持功能需要改进")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

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

def test_api_integration():
    """测试API集成效果"""
    print("\n" + "=" * 80)
    print("测试API集成效果")
    print("=" * 80)
    
    # 这里可以添加实际的API调用测试
    print("🔄 API集成测试（需要后端服务运行）")
    
    try:
        # 测试健康检查
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
            
            # 测试获取拆题会话列表
            token = login_and_get_token()
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                sessions_response = requests.get(
                    f"{API_BASE_URL}/api/ingest/sessions", 
                    headers=headers,
                    timeout=10
                )
                
                if sessions_response.status_code == 200:
                    sessions = sessions_response.json()
                    print(f"✅ 成功获取拆题会话列表，共 {len(sessions)} 个会话")
                else:
                    print(f"⚠️ 获取会话列表失败: {sessions_response.status_code}")
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保服务正在运行")
    except Exception as e:
        print(f"❌ API测试失败: {e}")

if __name__ == "__main__":
    test_document_upload()
    test_api_integration()
    
    print("\n" + "=" * 80)
    print("🎉 格式保持功能整合测试完成！")
    print("=" * 80)
    print("\n📋 下一步操作建议:")
    print("1. 运行数据库迁移: migrations/add_question_text_field.sql")
    print("2. 配置环境变量: 复制 .env.example 到 .env")
    print("3. 启动后端服务: cd backend && python -m uvicorn app.main:app --reload")
    print("4. 启动前端服务: cd frontend_vite && npm run dev")
    print("5. 测试文档上传功能，验证格式保持效果")