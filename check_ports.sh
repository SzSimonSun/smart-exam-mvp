#!/bin/bash

# 端口检查工具
echo "🔍 智能考试系统端口状态检查"
echo "================================"

check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -i :$port >/dev/null 2>&1; then
        local pid=$(lsof -ti :$port)
        local process=$(ps -p $pid -o comm= 2>/dev/null)
        echo "🔴 端口 $port ($service_name): 被占用 - PID: $pid ($process)"
        return 1
    else
        echo "🟢 端口 $port ($service_name): 空闲"
        return 0
    fi
}

# 检查主要端口
check_port 5173 "前端服务"
check_port 5174 "前端备用端口"
check_port 8000 "后端服务"

echo ""
echo "📊 PID文件状态:"
if [ -d ".pids" ]; then
    if [ -f ".pids/backend.pid" ]; then
        backend_pid=$(cat .pids/backend.pid)
        if kill -0 "$backend_pid" 2>/dev/null; then
            echo "🟢 后端PID文件存在且进程运行中: $backend_pid"
        else
            echo "🟡 后端PID文件存在但进程已停止: $backend_pid"
        fi
    else
        echo "⚪ 后端PID文件不存在"
    fi
    
    if [ -f ".pids/frontend.pid" ]; then
        frontend_pid=$(cat .pids/frontend.pid)
        if kill -0 "$frontend_pid" 2>/dev/null; then
            echo "🟢 前端PID文件存在且进程运行中: $frontend_pid"
        else
            echo "🟡 前端PID文件存在但进程已停止: $frontend_pid"
        fi
    else
        echo "⚪ 前端PID文件不存在"
    fi
else
    echo "⚪ PID目录不存在"
fi

echo ""
echo "💡 常用命令:"
echo "  ./start.sh         - 启动服务"
echo "  ./stop.sh          - 停止服务"
echo "  kill -9 <PID>      - 强制停止指定进程"
echo "  lsof -i :<PORT>    - 查看端口占用详情"