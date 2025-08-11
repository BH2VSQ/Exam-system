@echo off
REM 考试报名管理平台Windows部署脚本
REM 使用方法: deploy.bat [simple|full] [deploy|status|logs|stop|cleanup]

REM 强制CMD使用UTF-8编码
chcp 65001 > nul

setlocal enabledelayedexpansion

REM 颜色定义（Windows CMD不支持颜色，但可以用echo显示信息）
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM 检查Docker和Docker Compose
:check_dependencies
echo %INFO% 检查系统依赖...

docker --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Docker 未安装或未启动，请先安装并启动 Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Docker Compose 未安装，请确保 Docker Desktop 包含 Docker Compose
    pause
    exit /b 1
)

echo %SUCCESS% 系统依赖检查通过

REM 创建必要的目录
:create_directories
echo %INFO% 创建必要的目录...

if not exist "backend\uploads" mkdir "backend\uploads"
if not exist "backend\certificates" mkdir "backend\certificates"
if not exist "backend\src\database" mkdir "backend\src\database"
if not exist "nginx\ssl" mkdir "nginx\ssl"

echo %SUCCESS% 目录创建完成

REM 设置环境变量
:setup_environment
echo %INFO% 设置环境变量...

if not exist ".env" (
    echo # 生产环境配置 > .env
    echo FLASK_ENV=production >> .env
    echo SECRET_KEY=your-secret-key-change-in-production >> .env
    echo JWT_SECRET_KEY=your-jwt-secret-key-change-in-production >> .env
    echo. >> .env
    echo # 数据库配置 >> .env
    echo POSTGRES_DB=exam_system >> .env
    echo POSTGRES_USER=exam_user >> .env
    echo POSTGRES_PASSWORD=exam_password_change_in_production >> .env
    echo. >> .env
    echo # Redis配置 >> .env
    echo REDIS_URL=redis://redis:6379/0 >> .env
    echo. >> .env
    echo # 其他配置 >> .env
    echo UPLOAD_FOLDER=/app/uploads >> .env
    echo CERTIFICATE_FOLDER=/app/certificates >> .env
    echo MAX_CONTENT_LENGTH=16777216 >> .env
    
    echo %SUCCESS% 环境变量文件已创建
) else (
    echo %WARNING% 环境变量文件已存在，跳过创建
)

REM 简化部署
:deploy_simple
if "%1"=="simple" (
    echo %INFO% 开始简化部署（使用SQLite数据库）...
    
    REM 停止现有服务
    docker-compose -f docker-compose.simple.yml down 2>nul
    
    REM 构建并启动服务
    docker-compose -f docker-compose.simple.yml up --build -d
    
    echo %SUCCESS% 简化部署完成！
    echo %INFO% 前端访问地址: http://localhost
    echo %INFO% 后端API地址: http://localhost:5001
    echo %INFO% 默认管理员账号: admin / admin123
    goto :show_status_simple
)

REM 完整部署
:deploy_full
if "%1"=="full" (
    echo %INFO% 开始完整部署（使用PostgreSQL数据库）...
    
    REM 停止现有服务
    docker-compose down 2>nul
    
    REM 构建并启动服务
    docker-compose up --build -d
    
    echo %SUCCESS% 完整部署完成！
    echo %INFO% 前端访问地址: http://localhost
    echo %INFO% 后端API地址: http://localhost:5001
    echo %INFO% 数据库地址: localhost:5432
    echo %INFO% Redis地址: localhost:6379
    echo %INFO% 默认管理员账号: admin / admin123
    goto :show_status_full
)

REM 显示服务状态
:show_status_simple
if "%2"=="status" (
    echo %INFO% 服务状态:
    docker-compose -f docker-compose.simple.yml ps
    goto :end
)
goto :end

:show_status_full
if "%2"=="status" (
    echo %INFO% 服务状态:
    docker-compose ps
    goto :end
)
goto :end

REM 显示日志
:show_logs
if "%2"=="logs" (
    echo %INFO% 显示服务日志:
    if "%1"=="simple" (
        docker-compose -f docker-compose.simple.yml logs -f
    ) else (
        docker-compose logs -f
    )
    goto :end
)

REM 停止服务
:stop_services
if "%2"=="stop" (
    echo %INFO% 停止服务...
    if "%1"=="simple" (
        docker-compose -f docker-compose.simple.yml down
    ) else (
        docker-compose down
    )
    echo %SUCCESS% 服务已停止
    goto :end
)

REM 清理数据
:cleanup
if "%2"=="cleanup" (
    echo %WARNING% 这将删除所有数据，包括数据库和上传的文件！
    set /p confirm="确定要继续吗？(y/N): "
    if /i "!confirm!"=="y" (
        if "%1"=="simple" (
            docker-compose -f docker-compose.simple.yml down -v
        ) else (
            docker-compose down -v
        )
        if exist "backend\src\database" rmdir /s /q "backend\src\database"
        if exist "backend\uploads" rmdir /s /q "backend\uploads"
        if exist "backend\certificates" rmdir /s /q "backend\certificates"
        mkdir "backend\src\database"
        mkdir "backend\uploads"
        mkdir "backend\certificates"
        echo %SUCCESS% 数据清理完成
    ) else (
        echo %INFO% 取消清理操作
    )
    goto :end
)

REM 主逻辑
:main
echo ==========================================
echo     考试报名管理平台Windows部署脚本
echo ==========================================

set MODE=%1
set ACTION=%2

if "%MODE%"=="" set MODE=simple
if "%ACTION%"=="" set ACTION=deploy

if "%ACTION%"=="deploy" (
    call :check_dependencies
    call :create_directories
    call :setup_environment
    
    if "%MODE%"=="simple" (
        call :deploy_simple
    ) else if "%MODE%"=="full" (
        call :deploy_full
    ) else (
        echo %ERROR% 无效的部署模式: %MODE%
        echo 使用方法: %0 [simple^|full] [deploy^|status^|logs^|stop^|cleanup]
        pause
        exit /b 1
    )
) else if "%ACTION%"=="status" (
    call :show_status_%MODE%
) else if "%ACTION%"=="logs" (
    call :show_logs
) else if "%ACTION%"=="stop" (
    call :stop_services
) else if "%ACTION%"=="cleanup" (
    call :cleanup
) else (
    echo %ERROR% 无效的操作: %ACTION%
    echo 使用方法: %0 [simple^|full] [deploy^|status^|logs^|stop^|cleanup]
    pause
    exit /b 1
)

:end
pause

