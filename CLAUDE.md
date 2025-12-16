# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Django TLIAS (智能学习辅助系统) 是一个基于 Django 6.0 的后端管理系统，对标 Java Spring Boot 实现。项目采用了分层架构设计，提供部门管理、员工管理、学生管理、班级管理等功能模块。

## 常用开发命令

### 基础命令
```bash
# 激活虚拟环境
source venv/Scripts/activate  # Windows
source venv/bin/activate      # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python manage.py runserver 0.0.0.0:8000

# 数据库迁移（项目中使用 managed=False，不进行迁移）
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动 Django Shell
python manage.py shell
```

### 开发调试
```bash
# 查看SQL查询（需将settings.py中django.db.backends日志级别改为DEBUG）
# 日志文件位置: D:/项目日志记录/django-tlias/django-tlias.log

# 收集静态文件
python manage.py collectstatic

# 检查项目配置
python manage.py check --deploy
```

## 项目架构说明

### 目录结构
```
django-tlias/
├── django_tlias/          # 项目配置目录
│   ├── settings.py        # Django 主配置文件
│   ├── urls.py           # 主路由配置
│   └── wsgi.py           # WSGI 配置
├── management/           # 核心业务应用
│   ├── models/          # 数据模型（按模块拆分）
│   │   ├── emp.py       # 员工模型
│   │   ├── dept.py      # 部门模型
│   │   ├── student.py   # 学生模型
│   │   ├── clazz.py     # 班级模型
│   │   └── ...
│   ├── views/           # 视图层（Controller）
│   │   ├── dept_views.py
│   │   ├── emp_views.py
│   │   └── ...
│   ├── urls/            # 路由模块
│   │   ├── dept.py
│   │   ├── emp.py
│   │   └── ...
│   ├── services/        # 业务逻辑层（Service）
│   ├── serializers.py   # 序列化器
│   └── apps.py         # 应用配置
├── common/             # 公共模块
│   ├── result.py       # 统一响应结果
│   ├── jwt_utils.py    # JWT 工具类
│   ├── exceptions.py   # 异常处理
│   ├── log_decorator.py # 操作日志装饰器
│   └── auth_middleware.py # JWT 认证中间件
├── media/              # 文件上传目录
├── sql/                # SQL 脚本
│   ├── 01_schema.sql   # 表结构
│   └── 02_data.sql     # 初始数据
└── requirements.txt    # 依赖列表
```

### 分层设计
1. **Controller层 (views/)**: 极薄层，仅负责请求解析和响应封装
2. **Service层 (services/)**: 业务逻辑层，处理复杂业务规则
3. **Model层 (models/)**: 数据访问层，仅包含简单的CRUD操作

### 设计原则
- 对标 Java Spring Boot 架构
- 使用逻辑外键而非物理外键（避免级联删除问题）
- 所有模型设置 `managed = False`（使用现有数据库）
- 遵循 RESTful API 设计规范

## Django 配置详情

### 数据库配置
- 数据库：MySQL (tlias)
- 字符集：utf8mb4
- 驱动：mysqlclient
- 时区：Asia/Shanghai
- USE_TZ = False（与Java保持一致）

### REST Framework 配置
- 渲染器：CamelCaseJSONRenderer（输出自动转驼峰）
- 时间格式：yyyy-MM-dd HH:mm:ss
- 认证方式：自定义JWT（通过中间件实现）
- 异常处理：custom_exception_handler

### CORS 配置
- 允许前端：http://localhost:5173 (Vite开发服务器)
- 支持携带凭证

### 文件上传配置
- 上传路径：/media/
- 大小限制：10MB
- 兼容旧路径：/static/uploads/

### 日志配置
- 控制台输出：DEBUG级别
- 文件输出：INFO级别
- 日志文件：D:/项目日志记录/django-tlias/django-tlias.log
- 轮转策略：单文件10MB，保留30个

## 数据库模型结构

### 核心表结构

1. **员工表 (emp)**
   - username: 用户名（唯一）
   - password: 密码（MD5存储）
   - name: 姓名
   - gender: 性别（1:男, 2:女）
   - phone: 手机号（唯一）
   - job: 职位（2:班主任, 3:讲师, 4:学工主管, 5:教研主管）
   - salary: 薪资
   - image: 头像URL
   - entry_date: 入职日期
   - dept_id: 部门ID（逻辑外键）

2. **部门表 (dept)**
   - name: 部门名称（唯一）

3. **学生表 (student)**
   - name: 姓名
   - no: 学号（唯一）
   - gender: 性别
   - phone: 手机号
   - id_card: 身份证号
   - is_college: 是否院校生（1:是, 0:否）
   - degree: 学历（1:初中...6:博士）
   - violation_count: 违纪次数
   - violation_score: 违纪扣分
   - clazz_id: 班级ID

4. **班级表 (clazz)**
   - name: 班级名称
   - room: 教室
   - begin_date: 开课日期
   - end_date: 结课日期
   - master_id: 班主任ID
   - subject_id: 学科ID

5. **工作经历表 (emp_expr)**
   - emp_id: 员工ID
   - begin_date: 开始日期
   - end_date: 结束日期
   - company: 公司名称
   - job: 职位

### 关联关系
- 部门与员工：一对多（通过dept_id逻辑关联）
- 班级与学生：一对多（通过clazz_id逻辑关联）
- 员工与工作经历：一对多
- 班级与班主任：多对一（通过clazz.master_id）

## API 设计规范

### URL 设计
- 统一前缀：无（直接通过 path('', include('management.urls'))）引入
- RESTful 风格：使用名词复数形式
  - GET /depts - 查询列表
  - POST /depts - 新增
  - PUT /depts - 修改（ID在body中）
  - DELETE /depts?id=x - 删除（ID在query中）

### 响应格式
```json
{
  "code": 1,        // 1:成功, 0:失败
  "msg": "success", // 提示信息
  "data": {...}     // 响应数据
}
```

### 分页参数
- page: 页码（从1开始）
- pageSize: 每页数量
- name: 搜索关键字（模糊查询）

### 文件上传
- 单文件上传：/upload
- 多文件上传：/uploads
- 返回格式：文件URL数组

## 开发约定和最佳实践

### 代码规范
1. **命名规范**
   - 文件名：小写下划线（dept_views.py）
   - 类名：大驼峰（DeptListView）
   - 方法名：小写下划线（find_by_id）
   - 常量：大写下划线（MAX_FILE_SIZE）

2. **注释规范**
   - 类注释：说明职责和对标Java类
   - 方法注释：参数、返回值、异常说明
   - 行内注释：复杂逻辑说明

### 业务实现规范
1. **事务管理**
   - 使用 @transaction.atomic 装饰器
   - 事务边界控制在Service层

2. **异常处理**
   - 自定义业务异常：ServiceException
   - 全局异常处理器：common.exceptions.custom_exception_handler
   - 数据库异常转换为友好提示

3. **操作日志**
   - 使用 @log_operation 装饰器自动记录
   - 记录内容：操作人、时间、方法、参数、返回值、耗时

4. **JWT认证**
   - 密钥：aGV4aXh1ZXl1YW4= (Base64编码)
   - 过期时间：12小时
   - 中间件：common.auth_middleware.TokenAuthMiddleware

### 开发注意事项
1. **数据库操作**
   - 不使用Django的物理外键
   - 使用 objects.filter() 而非 objects.get()（避免异常）
   - 批量操作使用 bulk_create/bulk_update

2. **性能优化**
   - 查询优化：select_related/prefetch_related
   - 分页查询避免 offset 过大
   - 使用 defer/only 减少查询字段

3. **安全考虑**
   - 密码存储：MD5（需升级为bcrypt）
   - SQL注入：使用ORM参数化查询
   - XSS：DRF序列化器自动转义

### 调试技巧
1. **查看SQL**
   ```python
   from django.db import connection
   print(connection.queries)
   ```

2. **日志调试**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.debug('调试信息')
   ```

3. **Django Shell**
   ```python
   # 快速测试代码
   from management.models import Emp
   emp = Emp.objects.first()
   ```

## 扩展开发指南

### 新增功能模块步骤
1. 创建 models/xxx.py 定义模型
2. 创建 views/xxx_views.py 实现视图
3. 创建 urls/xxx.py 配置路由
4. 创建 services/xxx_service.py 实现业务逻辑
5. 在 serializers.py 添加序列化器
6. 在 management/urls.py 引入路由

### 常见问题解决
1. **跨域问题**：检查 CORS_ALLOWED_ORIGINS 配置
2. **文件上传403**：检查 CSRF 中间件（已禁用）
3. **数据库连接失败**：确认MySQL服务启动和配置正确
4. **JWT过期**：检查系统时间或调整 EXPIRE_HOURS

## 部署建议

### 开发环境
- 使用 manage.py runserver
- DEBUG = True
- 日志级别可调整为 DEBUG

### 生产环境
- 使用 Gunicorn + Nginx
- DEBUG = False
- 配置 ALLOWED_HOSTS
- 使用环境变量管理敏感配置
- 日志级别调整为 INFO 或 WARNING
- 配置日志轮转和备份策略

## 技术对标说明

本项目对标 Java Spring Boot 实现，主要技术点对应关系：

| 功能 | Django | Java Spring |
|------|--------|-------------|
| 依赖管理 | pip + requirements.txt | Maven/Gradle |
| 配置管理 | settings.py | application.yml |
| IOC容器 | 不适用 | Spring Container |
| AOP | 装饰器模式 | @Aspect 注解 |
| 事务管理 | @transaction.atomic | @Transactional |
| REST框架 | Django REST Framework | Spring MVC |
| JWT认证 | 自定义中间件 | Spring Security |
| 异常处理 | EXCEPTION_HANDLER | @ControllerAdvice |
| 日志框架 | logging模块 | Logback/SLF4J |
| ORM | Django ORM | MyBatis/JPA |
| 模板引擎 | Django Template | Thymeleaf/FreeMarker |