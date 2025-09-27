import requests
import json

# 测试试卷拆分功能
def test_question_bank_upload():
    """测试题库模块的试卷拆分功能"""
    
    base_url = "http://localhost:8000"
    
    # 1. 登录获取token
    print("🔐 正在登录...")
    login_response = requests.post(f"{base_url}/api/auth/login", json={
        "email": "teacher@example.com",
        "password": "password"
    })
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 测试上传试卷文件创建拆分会话
    print("\n📤 测试上传试卷文件...")
    
    # 创建一个测试文件
    test_content = "这是一个测试的试卷PDF内容".encode('utf-8')
    files = {
        'file': ('test_paper.pdf', test_content, 'application/pdf')
    }
    
    upload_response = requests.post(
        f"{base_url}/api/ingest/sessions",
        files=files,
        headers=headers
    )
    
    if upload_response.status_code != 200:
        print(f"❌ 上传失败: {upload_response.text}")
        return False
    
    session_data = upload_response.json()
    session_id = session_data["id"]
    print(f"✅ 上传成功，会话ID: {session_id}")
    print(f"   会话详情: {json.dumps(session_data, indent=2, ensure_ascii=False)}")
    
    # 3. 获取拆分会话列表
    print("\n📋 获取拆分会话列表...")
    sessions_response = requests.get(
        f"{base_url}/api/ingest/sessions",
        headers=headers
    )
    
    if sessions_response.status_code != 200:
        print(f"❌ 获取会话列表失败: {sessions_response.text}")
        return False
    
    sessions = sessions_response.json()
    print(f"✅ 获取会话列表成功，共 {len(sessions)} 个会话")
    for session in sessions[:3]:  # 只显示前3个
        print(f"   - ID: {session['id']}, 名称: {session['name']}, 状态: {session['status']}")
    
    # 4. 获取拆分项目列表
    print(f"\n🔍 获取会话 {session_id} 的拆分项目...")
    items_response = requests.get(
        f"{base_url}/api/ingest/sessions/{session_id}/items",
        headers=headers
    )
    
    if items_response.status_code != 200:
        print(f"❌ 获取拆分项目失败: {items_response.text}")
        return False
    
    items = items_response.json()
    print(f"✅ 获取拆分项目成功，共 {len(items)} 个项目")
    
    pending_items = [item for item in items if item.get('review_status') == 'pending']
    print(f"   待审核项目: {len(pending_items)} 个")
    
    # 5. 测试审核通过一个项目
    if pending_items:
        item_id = pending_items[0]['id']
        print(f"\n✅ 测试审核通过项目 {item_id}...")
        
        approve_response = requests.post(
            f"{base_url}/api/ingest/items/{item_id}/approve",
            json={
                "stem": "这是一个测试题目：1+1等于几？",
                "type": "single",
                "difficulty": 2
            },
            headers=headers
        )
        
        if approve_response.status_code != 200:
            print(f"❌ 审核通过失败: {approve_response.text}")
        else:
            print("✅ 审核通过成功")
            print(f"   响应: {json.dumps(approve_response.json(), indent=2, ensure_ascii=False)}")
    
    # 6. 测试拒绝一个项目
    if len(pending_items) > 1:
        item_id = pending_items[1]['id']
        print(f"\n❌ 测试拒绝项目 {item_id}...")
        
        reject_response = requests.post(
            f"{base_url}/api/ingest/items/{item_id}/reject",
            json={
                "reason": "题目质量不符合要求"
            },
            headers=headers
        )
        
        if reject_response.status_code != 200:
            print(f"❌ 拒绝失败: {reject_response.text}")
        else:
            print("✅ 拒绝成功")
            print(f"   响应: {json.dumps(reject_response.json(), indent=2, ensure_ascii=False)}")
    
    # 7. 再次获取项目列表查看状态变化
    print(f"\n🔄 再次检查项目状态...")
    updated_items_response = requests.get(
        f"{base_url}/api/ingest/sessions/{session_id}/items",
        headers=headers
    )
    
    if updated_items_response.status_code == 200:
        updated_items = updated_items_response.json()
        status_counts = {}
        for item in updated_items:
            status = item.get('review_status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("📊 项目状态统计:")
        for status, count in status_counts.items():
            print(f"   {status}: {count} 个")
    
    print("\n🎉 试卷拆分功能测试完成！")
    return True

if __name__ == "__main__":
    test_question_bank_upload()