#!/usr/bin/env python3
"""
测试试卷拆分API的调试脚本
"""

import requests
import json

# 1. 登录获取token
print("1. 测试登录...")
login_response = requests.post(
    "http://localhost:8001/api/auth/login",
    json={"email": "teacher@example.com", "password": "password"}
)
print(f"登录响应状态: {login_response.status_code}")
print(f"登录响应: {login_response.text}")

if login_response.status_code != 200:
    print("❌ 登录失败")
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ 获取到token: {token}")

# 2. 测试上传文件
print("\n2. 测试文件上传...")
headers = {"Authorization": f"Bearer {token}"}

with open("test_paper.pdf", "rb") as f:
    files = {"file": ("test_paper.pdf", f, "application/pdf")}
    
    try:
        upload_response = requests.post(
            "http://localhost:8001/api/ingest/sessions",
            headers=headers,
            files=files,
            timeout=30
        )
        
        print(f"上传响应状态: {upload_response.status_code}")
        print(f"上传响应: {upload_response.text}")
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            print(f"✅ 上传成功，会话ID: {result.get('id')}")
            
            # 3. 获取拆题结果
            session_id = result.get('id')
            if session_id:
                print(f"\n3. 获取拆题结果...")
                items_response = requests.get(
                    f"http://localhost:8001/api/ingest/sessions/{session_id}/items",
                    headers=headers
                )
                print(f"拆题结果状态: {items_response.status_code}")
                print(f"拆题结果: {items_response.text}")
        else:
            print(f"❌ 上传失败: {upload_response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

print("\n测试完成")