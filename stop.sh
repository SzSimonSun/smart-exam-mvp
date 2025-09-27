#!/bin/bash

# 智能考试系统停止脚本
# 使用PID文件精确停止服务

PID_DIR=".pids"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

echo "🛑 正在停止智能考试系统..."

# 停止后端服务
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "📛 停止后端服务 (PID: $BACKEND_PID)..."
        kill -TERM "$BACKEND_PID" 2>/dev/null
        # 等待2秒，如果还没停止就强制杀死
        sleep 2
        if kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo "⚠️  强制停止后端服务..."
            kill -9 "$BACKEND_PID" 2>/dev/null
        fi
        echo "✅ 后端服务已停止"
    else
        echo "⚠️  后端服务已经停止"
    fi
    rm -f "$BACKEND_PID_FILE"
else
    echo "🔍 未找到后端PID文件，尝试其他方式停止..."
    pkill -f "uvicorn.*app.main:app" 2>/dev/null && echo "✅ 通过pkill停止后端服务"
fi

# 停止前端服务
if [ -f "$FRONTEND_PID_FILE" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "📛 停止前端服务 (PID: $FRONTEND_PID)..."
        kill -TERM "$FRONTEND_PID" 2>/dev/null
        # 等待2秒，如果还没停止就强制杀死
        sleep 2
        if kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo "⚠️  强制停止前端服务..."
            kill -9 "$FRONTEND_PID" 2>/dev/null
        fi
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  前端服务已经停止"
    fi
    rm -f "$FRONTEND_PID_FILE"
else
    echo "🔍 未找到前端PID文件，尝试其他方式停止..."
    pkill -f "vite.*frontend_vite" 2>/dev/null && echo "✅ 通过pkill停止前端服务"
    pkill -f "npm run dev" 2>/dev/null
fi

# 清理端口占用（保险措施）
echo "🔧 清理端口占用..."
if lsof -i :8000 >/dev/null 2>&1; then
    echo "清理端口8000占用..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
fi

if lsof -i :5173 >/dev/null 2>&1; then
    echo "清理端口5173占用..."
    lsof -ti :5173 | xargs kill -9 2>/dev/null || true
fi

if lsof -i :5174 >/dev/null 2>&1; then
    echo "清理端口5174占用..."
    lsof -ti :5174 | xargs kill -9 2>/dev/null || true
fi

# 清理PID目录
if [ -d "$PID_DIR" ]; then
    rm -rf "$PID_DIR"
fi

sleep 1

echo ""
echo "✅ 智能考试系统已完全停止"
echo "📊 端口状态检查:"
echo "  端口5173: $(lsof -i :5173 >/dev/null 2>&1 && echo '占用' || echo '空闲')"
echo "  端口5174: $(lsof -i :5174 >/dev/null 2>&1 && echo '占用' || echo '空闲')"
echo "  端口8000: $(lsof -i :8000 >/dev/null 2>&1 && echo '占用' || echo '空闲')"