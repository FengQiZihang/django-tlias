"""
Django settings for django_tlias project.

Django Tlias 智能学习辅助系统 - 配置文件
"""

from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


# 安全配置
SECRET_KEY = 'django-insecure-3vv0i&xlyp=v70#240bb1zm2ypm9aw36hg(%4(5_qq@c(0uywc'
DEBUG = True
ALLOWED_HOSTS = ['*']


# 应用配置
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方应用
    'rest_framework',
    'corsheaders',
    # 项目应用
    'management',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS 中间件，必须放在最前面
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',  # 暂时禁用 CSRF（API 开发阶段）
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.auth_middleware.TokenAuthMiddleware',  # JWT 认证中间件
]

ROOT_URLCONF = 'django_tlias.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_tlias.wsgi.application'


# 数据库配置 - 连接现有的 MySQL tlias 数据库
# 使用 mysqlclient 作为 MySQL 驱动

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tlias',
        'USER': 'root',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}


# 密码验证（保留默认配置）
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# 国际化配置
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = False  # 使用本地时间，与 Java 后端保持一致


# 静态文件
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 上传文件配置 - 对标 Java application.yml
# 使用标准的 /media/ 路径，与 static 静态资源分离
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 文件上传大小限制 - 对标 Java max-file-size: 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB


# CORS 配置 - 允许前端开发服务器访问
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vite 开发服务器
    'http://127.0.0.1:5173',
]
CORS_ALLOW_CREDENTIALS = True


# Django REST Framework 配置
REST_FRAMEWORK = {
    # 全局驼峰命名渲染器 - 输出时 snake_case 转为 camelCase
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
    ),
    # 全局时间格式 - 对标 Java JacksonTimeConfig（yyyy-MM-dd HH:mm:ss）
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
    'TIME_FORMAT': '%H:%M:%S',
    # 暂时不设置认证
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    # 全局异常处理器 - 对标 Java GlobalExceptionHandler
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
}


# 日志配置 - 对标 Java logback.xml
# 日志文件目录（与 Java 保持一致）
LOG_DIR = Path('D:/项目日志记录/django-tlias')
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    # 格式化器 - 对标 logback 的 pattern
    'formatters': {
        # 控制台格式（简洁版）
        'console': {
            'format': '{asctime} [{process}] {levelname:<5} {name} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        # 文件格式（详细版，对标 logback 的 file pattern）
        'file': {
            'format': '{asctime}.{msecs:03.0f} [{process}] {levelname:<5} {name} - {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    
    # 处理器
    'handlers': {
        # 控制台输出 - 对标 logback 的 STDOUT appender
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        # 文件输出 - 对标 logback 的 RollingFileAppender
        # 使用 RotatingFileHandler: 单文件最大 10MB，保留 30 个备份
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django-tlias.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB，对标 logback 的 maxFileSize
            'backupCount': 30,              # 保留 30 个，对标 logback 的 MaxHistory
            'formatter': 'file',
            'encoding': 'utf-8',
        },
    },
    
    # 日志记录器
    'loggers': {
        # 项目应用日志
        'management': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'utils': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        # Django 框架日志
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        # 数据库查询日志（开发时可改为 DEBUG 查看 SQL）
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    
    # 根日志记录器 - 对标 logback 的 <root level="INFO">
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
