# Windows 系统部署指南

本文档详细说明如何在Windows系统上部署考试报名管理平台。

## 📋 系统要求

### 必需软件
- **Windows 10/11** (推荐)
- **Docker Desktop for Windows** 4.0+
- **Git for Windows** (可选，用于克隆代码)

### 硬件要求
- **内存**: 4GB+ (推荐8GB+)
- **磁盘空间**: 10GB+
- **网络**: 稳定的互联网连接

## 🚀 快速开始

### 步骤1：安装Docker Desktop

1. **下载Docker Desktop**
   - 访问 [Docker官网](https://www.docker.com/products/docker-desktop)
   - 下载 Docker Desktop for Windows
   - 运行安装程序并按照提示完成安装

2. **启动Docker Desktop**
   - 安装完成后启动Docker Desktop
   - 等待Docker引擎启动完成（系统托盘图标变为绿色）
   - 确保Docker Desktop正在运行

3. **验证安装**
   打开命令提示符(CMD)或PowerShell，运行：
   ```cmd
   docker --version
   docker-compose --version
   ```
   如果显示版本信息，说明安装成功。

### 步骤2：获取项目代码

**方式一：使用Git克隆（推荐）**
```cmd
git clone https://github.com/BH2VSQ/Exam-system.git
cd Exam-system
```

**方式二：下载ZIP文件**
1. 访问 https://github.com/BH2VSQ/Exam-system
2. 点击绿色的 "Code" 按钮
3. 选择 "Download ZIP"
4. 解压到您选择的目录

### 步骤3：部署应用

在项目根目录下，打开命令提示符(CMD)或PowerShell：

**简化部署（推荐新手）**
```cmd
deploy.bat simple
```

**完整部署（生产环境）**
```cmd
deploy.bat full
```

### 步骤4：访问应用

部署完成后，您可以通过以下地址访问：

- **前端界面**: http://localhost
- **后端API**: http://localhost:5001
- **默认管理员账号**: `admin` / `admin123`

## 🛠️ 详细操作指南

### 使用Windows批处理脚本

项目提供了 `deploy.bat` 脚本，支持以下操作：

```cmd
# 简化部署
deploy.bat simple deploy

# 完整部署
deploy.bat full deploy

# 查看服务状态
deploy.bat simple status
deploy.bat full status

# 查看服务日志
deploy.bat simple logs
deploy.bat full logs

# 停止服务
deploy.bat simple stop
deploy.bat full stop

# 清理所有数据（谨慎使用）
deploy.bat simple cleanup
deploy.bat full cleanup
```

### 手动使用Docker Compose

如果您更喜欢手动操作，可以直接使用Docker Compose命令：

**简化部署**
```cmd
# 停止现有服务
docker-compose -f docker-compose.simple.yml down

# 构建并启动服务
docker-compose -f docker-compose.simple.yml up --build -d

# 查看服务状态
docker-compose -f docker-compose.simple.yml ps

# 查看日志
docker-compose -f docker-compose.simple.yml logs -f
```

**完整部署**
```cmd
# 停止现有服务
docker-compose down

# 构建并启动服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 🔧 配置说明

### 环境变量配置

首次运行时，脚本会自动创建 `.env` 文件。您可以根据需要修改以下配置：

```env
# Flask配置
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# 数据库配置（仅完整部署）
POSTGRES_DB=exam_system
POSTGRES_USER=exam_user
POSTGRES_PASSWORD=exam_password_change_in_production

# 文件上传配置
UPLOAD_FOLDER=/app/uploads
CERTIFICATE_FOLDER=/app/certificates
MAX_CONTENT_LENGTH=16777216
```

### 端口配置

默认端口分配：
- **前端**: 80 (http://localhost)
- **后端**: 5001 (http://localhost:5001)
- **数据库**: 5432 (仅完整部署)
- **Redis**: 6379 (仅完整部署)

如果端口冲突，您可以修改 `docker-compose.yml` 或 `docker-compose.simple.yml` 文件中的端口映射。

## 🐛 常见问题解决

### 问题1：Docker Desktop未启动
**错误信息**: `error during connect: This error may indicate that the docker daemon is not running`

**解决方案**:
1. 确保Docker Desktop已启动
2. 检查系统托盘中的Docker图标是否为绿色
3. 重启Docker Desktop

### 问题2：端口被占用
**错误信息**: `port is already allocated`

**解决方案**:
1. 检查是否有其他服务占用80或5001端口
2. 停止占用端口的服务，或修改docker-compose文件中的端口映射
3. 使用 `netstat -ano | findstr :80` 查看端口占用情况

### 问题3：内存不足
**错误信息**: `not enough memory`

**解决方案**:
1. 关闭不必要的应用程序释放内存
2. 在Docker Desktop设置中增加内存分配
3. 重启计算机

### 问题4：网络连接问题
**错误信息**: `network timeout` 或下载失败

**解决方案**:
1. 检查网络连接
2. 配置Docker镜像加速器（中国用户推荐）
3. 重试部署命令

### 问题5：权限问题
**错误信息**: `permission denied`

**解决方案**:
1. 以管理员身份运行命令提示符
2. 确保Docker Desktop有足够的权限
3. 检查文件夹权限设置

## 📊 性能优化

### Docker Desktop设置优化

1. **内存分配**: 建议分配至少4GB内存给Docker
2. **CPU核心**: 分配2-4个CPU核心
3. **磁盘空间**: 确保有足够的磁盘空间用于镜像和容器

### Windows系统优化

1. **关闭不必要的服务**: 释放系统资源
2. **使用SSD**: 提高I/O性能
3. **定期清理**: 清理Docker镜像和容器

## 🔒 安全建议

1. **修改默认密码**: 部署后立即修改管理员密码
2. **更新密钥**: 修改 `.env` 文件中的密钥
3. **防火墙设置**: 配置Windows防火墙规则
4. **定期备份**: 备份重要数据和配置

## 📞 技术支持

如果您在部署过程中遇到问题：

1. 查看本文档的常见问题部分
2. 检查Docker Desktop日志
3. 查看应用日志：`deploy.bat simple logs`
4. 在GitHub仓库中提交Issue

## 🎯 下一步

部署成功后，您可以：

1. 使用默认管理员账号登录系统
2. 创建考试和配置报名表单
3. 测试报名和审核流程
4. 配置证书模板和编号规则
5. 导入测试数据进行功能验证

---

**注意**: 本指南适用于开发和测试环境。生产环境部署请参考项目主文档中的安全配置建议。

