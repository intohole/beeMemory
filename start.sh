#!/bin/bash

# 基于大模型的轻量化记忆系统启动脚本

# 默认配置
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8080"
DEFAULT_ENV="development"
DEFAULT_CONFIG="config.yaml"

# 显示帮助信息
show_help() {
    echo "基于大模型的轻量化记忆系统启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --host <host>          设置主机地址，默认: $DEFAULT_HOST"
    echo "  -p, --port <port>          设置端口号，默认: $DEFAULT_PORT"
    echo "  -e, --env <env>            设置运行环境 (development/production)，默认: $DEFAULT_ENV"
    echo "  -c, --config <file>        设置配置文件路径，默认: $DEFAULT_CONFIG"
    echo "  --help                     显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --port 8000 --env production"
    echo "  $0 --host 127.0.0.1 --port 8081 --config config.prod.yaml"
    echo ""
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -e|--env)
            ENV="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 设置默认值
HOST=${HOST:-$DEFAULT_HOST}
PORT=${PORT:-$DEFAULT_PORT}
ENV=${ENV:-$DEFAULT_ENV}
CONFIG=${CONFIG:-$DEFAULT_CONFIG}

# 检查配置文件是否存在
if [ ! -f "$CONFIG" ]; then
    echo "错误: 配置文件 $CONFIG 不存在!"
    echo "您可以从模板创建配置文件: cp config.example.yaml $CONFIG"
    exit 1
fi

# 设置环境变量
export ENVIRONMENT="$ENV"
export CONFIG_FILE="$CONFIG"

# 显示启动信息
echo "=========================================="
echo "基于大模型的轻量化记忆系统启动脚本"
echo "=========================================="
echo "运行环境: $ENV"
echo "配置文件: $CONFIG"
echo "主机地址: $HOST"
echo "端口号: $PORT"
echo "=========================================="
echo ""

# 根据环境选择启动命令
if [ "$ENV" = "development" ]; then
    echo "开发环境启动中..."
    echo "使用命令: uvicorn app.main:app --host $HOST --port $PORT --reload"
    echo ""
    uvicorn app.main:app --host "$HOST" --port "$PORT" --reload
elif [ "$ENV" = "production" ]; then
    echo "生产环境启动中..."
    echo "使用命令: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind $HOST:$PORT"
    echo ""
    # 检查gunicorn是否安装
    if ! command -v gunicorn &> /dev/null; then
        echo "警告: gunicorn 未安装，正在使用uvicorn启动..."
        uvicorn app.main:app --host "$HOST" --port "$PORT"
    else
        gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind "$HOST:$PORT"
    fi
else
    echo "错误: 未知的运行环境: $ENV"
    echo "支持的环境: development, production"
    exit 1
fi