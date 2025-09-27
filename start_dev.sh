#!/bin/bash

# 智能考试系统开发环境启动脚本
echo "🚀 启动智能考试系统开发环境..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查进程是否在运行
check_process() {
    local port=$1
    local name=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口 $port 已被占用 ($name)${NC}"
        return 0
    else
        return 1
    fi
}

# 停止现有进程
stop_services() {
    echo "🛑 停止现有服务..."
    
    # 停止前端 (Vite)
    pkill -f "vite" 2>/dev/null
    
    # 停止后端 (uvicorn)
    pkill -f "uvicorn" 2>/dev/null
    
    # 等待进程完全停止
    sleep 2
}

# 启动后端
start_backend() {
    echo -e "${GREEN}🔧 启动后端服务器...${NC}"
    
    if check_process 8000 "Backend"; then
        echo "后端服务器已在运行"
        return 0
    fi
    
    cd "$SCRIPT_DIR/backend"
    
    # 检查 Python 环境 - 强制使用 Homebrew Python 3.11.6
    PYTHON="/opt/homebrew/bin/python3"
    if ! command -v $PYTHON &> /dev/null; then
        echo -e "${RED}❌ Homebrew Python 3.11.6 未找到，请安装: brew install python@3.11${NC}"
        return 1
    fi
    
    PYTHON_VERSION=$($PYTHON --version 2>&1)
    echo "使用 Python: $PYTHON ($PYTHON_VERSION)"
    
    # 启动后端 (在后台运行)
    nohup $PYTHON -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo "后端 PID: $BACKEND_PID"
    
    # 等待后端启动
    echo "等待后端启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/ >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端启动成功 (http://localhost:8000)${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ 后端启动失败${NC}"
    return 1
}

# 启动前端
start_frontend() {
    echo -e "${GREEN}🎨 启动前端服务器...${NC}"
    
    if check_process 5173 "Frontend"; then
        echo "前端服务器已在运行"
        return 0
    fi
    
    cd "$SCRIPT_DIR/frontend_vite"
    
    # 检查 Node.js 和 npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm 未找到${NC}"
        return 1
    fi
    
    # 安装依赖（如果需要）
    if [ ! -d "node_modules" ]; then
        echo "安装前端依赖..."
        npm install
    fi
    
    # 启动前端 (在后台运行)
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "前端 PID: $FRONTEND_PID"
    
    # 等待前端启动
    echo "等待前端启动..."
    for i in {1..30}; do
        if curl -s http://localhost:5173/ >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 前端启动成功 (http://localhost:5173)${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}❌ 前端启动失败${NC}"
    return 1
}

# 显示状态
show_status() {
    echo ""
    echo "📊 服务状态:"
    echo "================="
    
    if check_process 8000 "Backend"; then
        echo -e "${GREEN}✅ 后端: http://localhost:8000${NC}"
    else
        echo -e "${RED}❌ 后端: 未运行${NC}"
    fi
    
    if check_process 5173 "Frontend"; then
        echo -e "${GREEN}✅ 前端: http://localhost:5173${NC}"
    else
        echo -e "${RED}❌ 前端: 未运行${NC}"
    fi
    
    echo ""
    echo "📝 日志文件:"
    echo "- 后端日志: $SCRIPT_DIR/backend.log"
    echo "- 前端日志: $SCRIPT_DIR/frontend.log"
    echo ""
    echo "🛑 停止服务: $SCRIPT_DIR/stop_dev.sh"
}

# 主函数
main() {
    case "${1:-start}" in
        "start")
            stop_services
            
            if start_backend && start_frontend; then
                show_status
                echo -e "${GREEN}🎉 开发环境启动完成！${NC}"
                echo ""
                echo "💡 提示:"
                echo "- 访问前端: http://localhost:5173"
                echo "- 访问后端API文档: http://localhost:8000/docs"
                echo "- 查看日志: tail -f backend.log frontend.log"
            else
                echo -e "${RED}❌ 启动失败${NC}"
                exit 1
            fi
            ;;
        "status")
            show_status
            ;;
        "stop")
            stop_services
            echo -e "${GREEN}✅ 服务已停止${NC}"
            ;;
        *)
            echo "用法: $0 [start|status|stop]"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"