"""
路由模块
"""

from .dept import urlpatterns as dept_urls
from .emp import urlpatterns as emp_urls
from .upload import urlpatterns as upload_urls
from .clazz import urlpatterns as clazz_urls
from .student import urlpatterns as student_urls
from .report import urlpatterns as report_urls
from .login import urlpatterns as login_urls

urlpatterns = login_urls + dept_urls + emp_urls + upload_urls + clazz_urls + student_urls + report_urls
