# 考试报名管理平台

一个高自定义化程度的前后端分离考试报名管理平台，支持大流量负荷、管理员账号管理、自定义考试信息和报名表单、准考证生成、成绩查询、证书编号管理等功能。

## 🚀 功能特性

### 核心功能
- **用户管理**: 支持管理员和普通用户角色，完整的用户认证和授权系统
- **考试管理**: 创建、编辑、删除考试信息，支持自定义考试类型和时间安排
- **报名管理**: 灵活的报名表单配置，支持文件上传和自定义字段
- **成绩管理**: 批量导入成绩，支持成绩查询和统计分析
- **证书管理**: 自动生成证书编号，支持证书模板自定义

### 高级功能
- **证书更替**: 支持换证和补证申请，完整的审核流程
- **准考证生成**: 可自定义准考证模板和内容
- **动态表单**: 支持自定义报名表单字段和验证规则
- **高并发支持**: 优化的数据库设计和缓存策略
- **文件管理**: 支持多种文件格式上传和管理

### 技术特性
- **前后端分离**: React + Flask 架构
- **响应式设计**: 支持桌面和移动设备
- **Docker部署**: 一键部署，支持容器化运行
- **数据库支持**: SQLite（开发）/ PostgreSQL（生产）
- **安全性**: JWT认证，CORS支持，输入验证

## 📋 系统要求

### 开发环境
- Node.js 20+
- Python 3.11+
- pnpm 或 npm

### 生产环境
- Docker 20+
- Docker Compose 2+
- 2GB+ RAM
- 10GB+ 磁盘空间

## 🛠️ 快速开始

### 方式一：Docker 一键部署（推荐）

1. **克隆项目**
   ```bash
   git clone git@github.com:BH2VSQ/Exam-system.git
   cd Exam-system
   ```

2. **简化部署（使用SQLite）**
   ```bash
   ./deploy.sh simple
   ```

3. **完整部署（使用PostgreSQL）**
   ```bash
   ./deploy.sh full
   ```

4. **访问应用**
   - 前端: http://localhost
   - 后端API: http://localhost:5001
   - 默认管理员账号: `admin` / `admin123`

### 方式二：开发环境部署

1. **后端设置**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python src/main.py
   ```

2. **前端设置**
   ```bash
   cd frontend
   pnpm install
   pnpm run dev
   ```

3. **访问应用**
   - 前端: http://localhost:5173
   - 后端API: http://localhost:5001

## 📚 使用指南

### 管理员功能

1. **考试管理**
   - 创建新考试，设置考试时间、地点、类型
   - 配置报名表单字段和验证规则
   - 管理考试状态和报名人数限制

2. **报名管理**
   - 查看所有报名申请
   - 审核报名资料和文件
   - 批量导入和导出报名数据

3. **成绩管理**
   - 批量导入考试成绩
   - 设置成绩查询权限
   - 生成成绩统计报告

4. **证书管理**
   - 批量生成证书编号
   - 自定义证书模板
   - 处理证书更替申请

### 用户功能

1. **考试报名**
   - 浏览可报名的考试
   - 填写报名表单和上传文件
   - 查看报名状态和审核结果

2. **成绩查询**
   - 查看个人考试成绩
   - 下载成绩单

3. **证书管理**
   - 查看个人证书
   - 下载证书文件
   - 申请证书更替（换证/补证）

## 🔧 配置说明

### 环境变量

创建 `.env` 文件配置以下变量：

```env
# Flask配置
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# 数据库配置
DATABASE_URL=sqlite:///app.db
# 或使用PostgreSQL: postgresql://user:password@localhost:5432/dbname

# 文件上传配置
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=16777216

# 证书配置
CERTIFICATE_FOLDER=/app/certificates
```

### 数据库配置

**SQLite（默认）**
- 适用于开发和小规模部署
- 数据文件位于 `backend/src/database/app.db`

**PostgreSQL（生产推荐）**
- 适用于生产环境和大规模部署
- 支持并发访问和数据备份

## 🚀 部署指南

### Docker 部署

1. **简化部署**
   ```bash
   # 使用SQLite数据库，快速启动
   ./deploy.sh simple deploy
   
   # 查看服务状态
   ./deploy.sh simple status
   
   # 查看日志
   ./deploy.sh simple logs
   
   # 停止服务
   ./deploy.sh simple stop
   ```

2. **生产部署**
   ```bash
   # 使用PostgreSQL数据库，完整功能
   ./deploy.sh full deploy
   
   # 查看服务状态
   ./deploy.sh full status
   
   # 查看日志
   ./deploy.sh full logs
   
   # 停止服务
   ./deploy.sh full stop
   ```

### 手动部署

1. **构建镜像**
   ```bash
   # 构建后端镜像
   docker build -t exam-system-backend ./backend
   
   # 构建前端镜像
   docker build -t exam-system-frontend ./frontend
   ```

2. **运行容器**
   ```bash
   # 启动后端
   docker run -d -p 5001:5001 --name backend exam-system-backend
   
   # 启动前端
   docker run -d -p 80:80 --name frontend exam-system-frontend
   ```

## 🔍 API 文档

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/auth/profile` - 获取用户信息

### 考试接口
- `GET /api/exams` - 获取考试列表
- `POST /api/exams` - 创建考试（管理员）
- `GET /api/exams/{id}` - 获取考试详情
- `PUT /api/exams/{id}` - 更新考试（管理员）

### 报名接口
- `POST /api/applications` - 提交报名申请
- `GET /api/applications` - 获取我的报名
- `GET /api/exams/{id}/applications` - 获取考试报名列表（管理员）

### 成绩接口
- `GET /api/my-scores` - 获取我的成绩
- `POST /api/scores/import` - 导入成绩（管理员）

### 证书接口
- `GET /api/certificates/my-certificates` - 获取我的证书
- `POST /api/certificates/generate` - 生成证书（管理员）
- `POST /api/certificates/renewal-application` - 申请证书更替

## 🛡️ 安全说明

1. **认证安全**
   - 使用JWT令牌进行身份验证
   - 密码使用bcrypt加密存储
   - 支持令牌过期和刷新

2. **数据安全**
   - 输入验证和SQL注入防护
   - 文件上传类型和大小限制
   - CORS配置和XSS防护

3. **部署安全**
   - 生产环境请修改默认密钥
   - 使用HTTPS加密传输
   - 定期备份数据库

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持

如果您在使用过程中遇到问题，请：

1. 查看 [Issues](https://github.com/BH2VSQ/Exam-system/issues) 中的已知问题
2. 创建新的 Issue 描述您的问题
3. 联系项目维护者

## 🎯 路线图

- [ ] 移动端APP开发
- [ ] 微信小程序支持
- [ ] 多语言国际化
- [ ] 高级统计分析
- [ ] 第三方集成（钉钉、企业微信等）
- [ ] 人脸识别身份验证
- [ ] 在线考试功能

---

**开发团队**: Manus AI Assistant  
**项目地址**: https://github.com/BH2VSQ/Exam-system  
**更新时间**: 2025年8月

