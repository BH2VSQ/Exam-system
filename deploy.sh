#!/bin/bash

# 考试报名管理平台一键部署脚本
# 使用方法: ./deploy.sh [simple|full]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker和Docker Compose
check_dependencies() {
    log_info "检查系统依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "系统依赖检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p backend/uploads
    mkdir -p backend/certificates
    mkdir -p backend/src/database
    mkdir -p nginx/ssl
    
    log_success "目录创建完成"
}

# 设置环境变量
setup_environment() {
    log_info "设置环境变量..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# 生产环境配置
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 数据库配置
POSTGRES_DB=exam_system
POSTGRES_USER=exam_user
POSTGRES_PASSWORD=$(openssl rand -hex 16)

# Redis配置
REDIS_URL=redis://redis:6379/0

# 其他配置
UPLOAD_FOLDER=/app/uploads
CERTIFICATE_FOLDER=/app/certificates
MAX_CONTENT_LENGTH=16777216
EOF
        log_success "环境变量文件已创建"
    else
        log_warning "环境变量文件已存在，跳过创建"
    fi
}

# 构建和启动服务
deploy_simple() {
    log_info "开始简化部署（使用SQLite数据库）..."
    
    # 停止现有服务
    docker-compose -f docker-compose.simple.yml down 2>/dev/null || true
    
    # 构建并启动服务
    docker-compose -f docker-compose.simple.yml up --build -d
    
    log_success "简化部署完成！"
    log_info "前端访问地址: http://localhost"
    log_info "后端API地址: http://localhost:5001"
    log_info "默认管理员账号: admin / admin123"
}

# 完整部署
deploy_full() {
    log_info "开始完整部署（使用PostgreSQL数据库）..."
    
    # 停止现有服务
    docker-compose down 2>/dev/null || true
    
    # 构建并启动服务
    docker-compose up --build -d
    
    log_success "完整部署完成！"
    log_info "前端访问地址: http://localhost"
    log_info "后端API地址: http://localhost:5001"
    log_info "数据库地址: localhost:5432"
    log_info "Redis地址: localhost:6379"
    log_info "默认管理员账号: admin / admin123"
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    if [ "$1" = "simple" ]; then
        docker-compose -f docker-compose.simple.yml ps
    else
        docker-compose ps
    fi
}

# 显示日志
show_logs() {
    log_info "显示服务日志:"
    if [ "$1" = "simple" ]; then
        docker-compose -f docker-compose.simple.yml logs -f
    else
        docker-compose logs -f
    fi
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    if [ "$1" = "simple" ]; then
        docker-compose -f docker-compose.simple.yml down
    else
        docker-compose down
    fi
    log_success "服务已停止"
}

# 清理数据
cleanup() {
    log_warning "这将删除所有数据，包括数据库和上传的文件！"
    read -p "确定要继续吗？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$1" = "simple" ]; then
            docker-compose -f docker-compose.simple.yml down -v
        else
            docker-compose down -v
        fi
        rm -rf backend/src/database/*
        rm -rf backend/uploads/*
        rm -rf backend/certificates/*
        log_success "数据清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "    考试报名管理平台部署脚本"
    echo "=========================================="
    
    MODE=${1:-simple}
    ACTION=${2:-deploy}
    
    case $ACTION in
        "deploy")
            check_dependencies
            create_directories
            setup_environment
            
            case $MODE in
                "simple")
                    deploy_simple
                    show_status simple
                    ;;
                "full")
                    deploy_full
                    show_status full
                    ;;
                *)
                    log_error "无效的部署模式: $MODE"
                    echo "使用方法: $0 [simple|full] [deploy|status|logs|stop|cleanup]"
                    exit 1
                    ;;
            esac
            ;;
        "status")
            show_status $MODE
            ;;
        "logs")
            show_logs $MODE
            ;;
        "stop")
            stop_services $MODE
            ;;
        "cleanup")
            cleanup $MODE
            ;;
        *)
            log_error "无效的操作: $ACTION"
            echo "使用方法: $0 [simple|full] [deploy|status|logs|stop|cleanup]"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"

