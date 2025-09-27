#!/usr/bin/env python3
"""
测试拆题入库功能
"""

import sqlite3
import json
import requests
from datetime import datetime

def test_ingest_function():
    """测试拆题入库功能"""
    print("=== 测试拆题入库功能 ===")
    
    # 1. 检查数据库数据
    print("\n1. 检查数据库数据...")
    try:
        conn = sqlite3.connect('/Users/sunfei/smart-exam-mvp/test_exam.db')
        cursor = conn.cursor()
        
        # 检查会话数据
        cursor.execute("""
            SELECT id, created_by, status, total_items, processed_items 
            FROM ingest_sessions 
            ORDER BY id DESC LIMIT 3
        """)
        sessions = cursor.fetchall()
        
        print(f"✅ 找到 {len(sessions)} 个拆题会话:")
        for session_id, created_by, status, total_items, processed_items in sessions:
            print(f"   会话 {session_id}: created_by={created_by}, 状态={status}, 总题目={total_items}")
        
        # 检查拆题项目数据
        if sessions:
            latest_session_id = sessions[0][0]
            cursor.execute("""
                SELECT id, seq, candidate_type, review_status, 
                       substr(ocr_json, 1, 50) as text_preview,
                       confidence
                FROM ingest_items 
                WHERE session_id = ? 
                ORDER BY seq LIMIT 5
            """, (latest_session_id,))
            items = cursor.fetchall()
            
            print(f"\n✅ 会话 {latest_session_id} 中找到 {len(items)} 个拆题项目:")
            for item_id, seq, q_type, status, text_preview, confidence in items:
                print(f"   项目 {item_id}: seq={seq}, 类型={q_type}, 状态={status}")
                print(f"      文本预览: {text_preview}")
                print(f"      置信度: {confidence}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False
    
    # 2. 测试API访问（需要认证）
    print("\n2. 测试API认证...")
    try:
        # 测试登录
        login_response = requests.post('http://localhost:8000/api/auth/login', 
                                     json={'username': 'admin@example.com', 'password': 'password'})
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            print("✅ 登录成功，获取到token")
            
            # 测试获取拆题会话列表
            headers = {'Authorization': f'Bearer {token}'}
            sessions_response = requests.get('http://localhost:8000/api/ingest/sessions', headers=headers)
            
            if sessions_response.status_code == 200:
                sessions_data = sessions_response.json()
                print(f"✅ 成功获取拆题会话列表，共 {len(sessions_data)} 个会话")
                
                if sessions_data:
                    # 测试获取拆题项目
                    session_id = sessions_data[0]['id']
                    items_response = requests.get(f'http://localhost:8000/api/ingest/sessions/{session_id}/items', 
                                                headers=headers)
                    
                    if items_response.status_code == 200:
                        items_data = items_response.json()
                        print(f"✅ 成功获取拆题项目列表，共 {len(items_data)} 个项目")
                        
                        for item in items_data[:3]:  # 只显示前3个
                            print(f"   项目 {item['id']}: {item.get('question_text', '无文本')[:30]}...")
                    else:
                        print(f"❌ 获取拆题项目失败: {items_response.status_code}")
                        print(f"错误信息: {items_response.text}")
                else:
                    print("⚠️  拆题会话列表为空")
            else:
                print(f"❌ 获取拆题会话列表失败: {sessions_response.status_code}")
                print(f"错误信息: {sessions_response.text}")
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            print(f"错误信息: {login_response.text}")
            
    except Exception as e:
        print(f"❌ API测试失败: {e}")
    
    # 3. 建议解决方案
    print("\n3. 问题分析和解决建议:")
    print("如果前端看不到拆题会话内容，可能的原因:")
    print("1. 数据权限问题 - created_by字段不匹配当前用户ID")
    print("2. 认证问题 - token过期或无效") 
    print("3. 前端数据获取逻辑问题")
    print("4. 后端API权限配置问题")
    
    print("\n建议操作:")
    print("1. 确认当前登录用户ID是否为1")
    print("2. 检查浏览器控制台的网络请求和错误信息")
    print("3. 验证token是否有效")
    print("4. 刷新页面重新登录")

if __name__ == "__main__":
    test_ingest_function()