#!/usr/bin/env python3
"""
测试完整的拆题审核入库流程
"""

import requests
import json

def test_complete_ingest_workflow():
    base_url = "http://localhost:8000"
    token = "token_for_13_e64c7d89"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🧪 测试完整的拆题审核入库流程")
    print("=" * 50)
    
    # 1. 获取拆题会话列表
    print("1️⃣ 获取拆题会话列表...")
    sessions_response = requests.get(f"{base_url}/api/ingest/sessions", headers=headers)
    if sessions_response.status_code == 200:
        sessions = sessions_response.json()
        print(f"✅ 找到 {len(sessions)} 个拆题会话")
        if sessions:
            latest_session = sessions[0]
            session_id = latest_session['id']
            print(f"📋 使用会话: {latest_session['name']} (ID: {session_id})")
        else:
            print("❌ 没有找到拆题会话")
            return
    else:
        print(f"❌ 获取会话列表失败: {sessions_response.status_code}")
        return
    
    # 2. 获取拆题项目
    print(f"\n2️⃣ 获取会话 {session_id} 的拆题项目...")
    items_response = requests.get(f"{base_url}/api/ingest/sessions/{session_id}/items", headers=headers)
    if items_response.status_code == 200:
        items = items_response.json()
        print(f"✅ 找到 {len(items)} 个拆题项目")
        
        # 显示项目状态
        for item in items:
            status = item['review_status']
            text = item.get('question_text', '')[:50] + ('...' if len(item.get('question_text', '')) > 50 else '')
            print(f"  📝 项目 {item['id']}: {text} - 状态: {status}")
            
        # 找到一个待审核的项目
        pending_items = [item for item in items if item['review_status'] == 'pending']
        if pending_items:
            test_item = pending_items[0]
            item_id = test_item['id']
            print(f"🎯 选择项目 {item_id} 进行审核测试")
        else:
            print("⚠️ 没有找到待审核的项目")
            return
    else:
        print(f"❌ 获取拆题项目失败: {items_response.status_code}")
        return
    
    # 3. 测试审核通过
    print(f"\n3️⃣ 测试审核通过项目 {item_id}...")
    approval_data = {
        "stem": test_item.get('question_text', '测试题目'),
        "type": test_item.get('candidate_type', 'single'),
        "difficulty": 2
    }
    
    approve_response = requests.post(
        f"{base_url}/api/ingest/items/{item_id}/approve",
        headers={**headers, "Content-Type": "application/json"},
        json=approval_data
    )
    
    if approve_response.status_code == 200:
        result = approve_response.json()
        print(f"✅ 审核通过成功!")
        print(f"  📝 拆题项目 ID: {result['item_id']}")
        print(f"  📚 题库题目 ID: {result['question_id']}")
        question_id = result['question_id']
    else:
        print(f"❌ 审核通过失败: {approve_response.status_code}")
        print(f"响应内容: {approve_response.text}")
        return
    
    # 4. 验证题目是否成功添加到题库
    print(f"\n4️⃣ 验证题目是否添加到题库...")
    questions_response = requests.get(f"{base_url}/api/questions", headers=headers)
    if questions_response.status_code == 200:
        questions = questions_response.json()
        # 查找刚添加的题目
        added_question = None
        for q in questions:
            if q['id'] == question_id:
                added_question = q
                break
        
        if added_question:
            print(f"✅ 题目成功添加到题库!")
            print(f"  📝 题目内容: {added_question['stem'][:100]}...")
            print(f"  🏷️ 题目类型: {added_question['type']}")
            print(f"  ⭐ 难度等级: {added_question['difficulty']}")
            print(f"  📊 状态: {added_question['status']}")
        else:
            print(f"❌ 在题库中未找到题目 ID {question_id}")
    else:
        print(f"❌ 获取题库失败: {questions_response.status_code}")
        return
    
    # 5. 验证拆题项目状态更新
    print(f"\n5️⃣ 验证拆题项目状态更新...")
    updated_items_response = requests.get(f"{base_url}/api/ingest/sessions/{session_id}/items", headers=headers)
    if updated_items_response.status_code == 200:
        updated_items = updated_items_response.json()
        updated_item = None
        for item in updated_items:
            if item['id'] == item_id:
                updated_item = item
                break
        
        if updated_item:
            print(f"✅ 拆题项目状态更新成功!")
            print(f"  📊 审核状态: {updated_item['review_status']}")
            print(f"  🔗 关联题目 ID: {updated_item['approved_question_id']}")
        else:
            print(f"❌ 未找到拆题项目 ID {item_id}")
    else:
        print(f"❌ 获取更新后的拆题项目失败: {updated_items_response.status_code}")
    
    print("\n🎉 完整流程测试完成!")

if __name__ == "__main__":
    test_complete_ingest_workflow()