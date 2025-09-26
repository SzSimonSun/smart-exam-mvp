#!/bin/bash

# 测试答题卡上传功能
echo "🧪 测试答题卡上传功能..."

# 获取登录token
echo "📋 获取登录token..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "teacher@example.com", "password": "password"}' | \
  jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ 登录失败"
  exit 1
fi

echo "✅ 登录成功，Token: ${TOKEN:0:20}..."

# 创建测试文件
echo "📄 创建测试文件..."
echo "这是一个测试答题卡图片" > test_upload.jpg

# 测试上传
echo "📤 测试上传答题卡..."
UPLOAD_RESULT=$(curl -s -X POST \
  "http://localhost:8000/api/answer-sheets/upload?paper_id=1&class_id=1" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_upload.jpg")

echo "📊 上传结果: $UPLOAD_RESULT"

# 检查结果
if echo "$UPLOAD_RESULT" | grep -q "accepted"; then
  echo "✅ 答题卡上传测试通过！"
else
  echo "❌ 答题卡上传测试失败"
  echo "错误信息: $UPLOAD_RESULT"
fi

# 清理测试文件
rm -f test_upload.jpg

echo "🎉 测试完成！"