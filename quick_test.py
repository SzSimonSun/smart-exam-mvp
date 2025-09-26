#!/usr/bin/env python3
"""
智能试卷系统快速联调测试脚本
包含API测试、文件上传测试、Worker任务测试等
"""
import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_login():
    """测试登录功能"""
    print("🔐 测试登录功能...")
    
    login_data = {
        "email": "teacher@example.com",
        "password": "password"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ 登录成功，获取Token: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录请求异常: {e}")
        return None

def test_knowledge_points(token):
    """测试知识点API"""
    print("\n📚 测试知识点API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge-points", headers=headers)
        if response.status_code == 200:
            kps = response.json()
            print(f"✅ 获取知识点成功，总数: {len(kps)}")
            print(f"   示例: {kps[0]['subject']} > {kps[0]['module']} > {kps[0]['point']}")
            return True
        else:
            print(f"❌ 获取知识点失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 知识点请求异常: {e}")
        return False

def test_questions(token):
    """测试题目API"""
    print("\n📝 测试题目API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/questions", headers=headers)
        if response.status_code == 200:
            questions = response.json()
            print(f"✅ 获取题目成功，总数: {len(questions)}")
            for q in questions[:3]:
                print(f"   {q['id']}. {q['stem'][:30]}... ({q['type']}, 难度{q['difficulty']})")
            return questions
        else:
            print(f"❌ 获取题目失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 题目请求异常: {e}")
        return []

def test_create_question(token):
    """测试创建题目"""
    print("\n➕ 测试创建题目...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    new_question = {
        "stem": f"测试题目 - {datetime.now().strftime('%H:%M:%S')}：计算 5 + 7 = ?",
        "type": "single",
        "difficulty": 1,
        "options_json": {
            "A": "10",
            "B": "11", 
            "C": "12",
            "D": "13"
        },
        "answer_json": {
            "answer": "C"
        },
        "analysis": "简单的加法运算：5 + 7 = 12",
        "knowledge_point_ids": [1]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/questions", json=new_question, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 创建题目成功，ID: {result['id']}")
            return result
        else:
            print(f"❌ 创建题目失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 创建题目异常: {e}")
        return None

def test_file_upload(token):
    """测试文件上传（模拟答题卡上传）"""
    print("\n📤 测试文件上传...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建一个临时测试文件
    test_content = "This is a test image file for answer sheet upload."
    test_filename = "test_answer_sheet.txt"
    
    with open(test_filename, "w") as f:
        f.write(test_content)
    
    try:
        with open(test_filename, "rb") as f:
            files = {"file": (test_filename, f, "text/plain")}
            data = {
                "paper_id": 1,
                "class_id": 1
            }
            
            response = requests.post(
                f"{BASE_URL}/api/answer-sheets/upload",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 文件上传成功: {result['message']}")
                print(f"   文件名: {result['filename']}")
                return True
            else:
                print(f"❌ 文件上传失败: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 文件上传异常: {e}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(test_filename):
            os.remove(test_filename)

def test_report(token):
    """测试报表API"""
    print("\n📊 测试报表API...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/answer-sheets/1/report", headers=headers)
        if response.status_code == 200:
            report = response.json()
            print(f"✅ 获取报表成功")
            print(f"   学生: {report['student_name']}")
            print(f"   试卷: {report['paper_name']}")
            print(f"   总分: {report['total_score']}")
            return True
        else:
            print(f"❌ 获取报表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 报表请求异常: {e}")
        return False

def check_services():
    """检查服务状态"""
    print("🔍 检查服务状态...")
    
    services = {
        "后端API": f"{BASE_URL}/health",
        "前端应用": FRONTEND_URL,
        "API文档": f"{BASE_URL}/docs"
    }
    
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name}: 正常 ({url})")
            else:
                print(f"⚠️ {service_name}: 状态码 {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name}: 无法访问 - {e}")

def test_worker_simulation():
    """模拟Worker任务测试"""
    print("\n🤖 模拟Worker任务测试...")
    
    # 这里可以添加向RabbitMQ发送测试任务的代码
    # 由于需要额外的依赖，这里只是提示
    print("📝 Worker测试提示:")
    print("   1. 检查worker容器状态: docker logs smart_exam_omr_worker")
    print("   2. 检查队列状态: 访问 http://localhost:15672 (guest/guest)")
    print("   3. 手动测试: 使用 workers/test_workers.py 脚本")
    
    return True

def main():
    """主测试流程"""
    print("🚀 智能试卷系统快速联调测试")
    print("=" * 50)
    
    # 1. 检查服务状态
    check_services()
    
    # 2. 测试登录
    token = test_login()
    if not token:
        print("❌ 登录失败，终止测试")
        return
    
    # 3. 测试各个API
    test_knowledge_points(token)
    questions = test_questions(token)
    test_create_question(token)
    test_file_upload(token)
    test_report(token)
    
    # 4. Worker测试提示
    test_worker_simulation()
    
    print("\n" + "=" * 50)
    print("🎯 测试总结:")
    print("✅ 如果大部分测试通过，说明系统基本功能正常")
    print("📱 前端测试: 访问 http://localhost:5173 进行手动测试")
    print("📖 API文档: 访问 http://localhost:8000/docs 查看完整API")
    print("🔧 如有问题，请检查:")
    print("   - Docker容器是否都在运行")
    print("   - 数据库是否已导入测试数据")
    print("   - 网络连接是否正常")

if __name__ == "__main__":
    main()