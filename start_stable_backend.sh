#!/bin/bash

# 稳定的后端启动脚本
# 使用screen会话，即使终端关闭也能保持运行

BACKEND_DIR="/Users/sunfei/smart-exam-mvp/backend"
SESSION_NAME="smart_exam_backend"
LOG_FILE="/Users/sunfei/smart-exam-mvp/backend.log"

echo "🚀 启动智能考试系统后端服务..."

# 检查是否已有运行的会话
if screen -list | grep -q "$SESSION_NAME"; then
    echo "⚠️  检测到已运行的后端服务，先停止它..."
    screen -S "$SESSION_NAME" -X quit
    sleep 2
fi

# 清理可能的残留进程
pkill -f "uvicorn.*app.main" || true
sleep 1

# 切换到后端目录
cd "$BACKEND_DIR" || exit 1

# 创建新的screen会话并启动服务
echo "📱 创建新的screen会话: $SESSION_NAME"
screen -dmS "$SESSION_NAME" bash -c "
    echo '启动时间: $(date)' >> $LOG_FILE
    echo '工作目录: $(pwd)' >> $LOG_FILE
    python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --workers 1 2>&1 | tee -a $LOG_FILE
"

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 健康检查
echo "🏥 健康检查..."
if curl -s http://127.0.0.1:8001/health > /dev/null; then
    echo "✅ 后端服务启动成功！"
    echo "📋 服务信息:"
    echo "   - 地址: http://127.0.0.1:8001"
    echo "   - 健康检查: http://127.0.0.1:8001/health"
    echo "   - 日志文件: $LOG_FILE"
    echo "   - Screen会话: $SESSION_NAME"
    echo ""
    echo "📝 管理命令:"
    echo "   查看日志: tail -f $LOG_FILE"
    echo "   查看会话: screen -r $SESSION_NAME"
    echo "   停止服务: screen -S $SESSION_NAME -X quit"
    echo ""
    curl -s http://127.0.0.1:8001/health
else
    echo "❌ 服务启动失败，查看日志："
    tail -20 "$LOG_FILE"
    exit 1
fi