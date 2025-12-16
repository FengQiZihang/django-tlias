"""
Django Tlias 项目主路由配置

前端通过 /api/* 访问后端接口
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # API 路由 - 对应前端 /api/* 请求
    path('', include('management.urls')),
]

# 开发模式下提供静态文件服务（生产环境应由 Nginx 等处理）
if settings.DEBUG:
    urlpatterns += static('/static/', document_root=settings.BASE_DIR / 'static')
    # 提供上传文件的 HTTP 服务（新路径）
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 兼容旧路径：数据库中已存储的 /static/uploads/... URL
    urlpatterns += static('/static/uploads/', document_root=settings.BASE_DIR / 'static' / 'uploads')
