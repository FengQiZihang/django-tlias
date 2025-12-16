"""
服务模块
"""

from .dept_service import DeptService
from .emp_service import EmpService
from .emp_log_service import EmpLogService
from .upload_service import UploadService
from .clazz_service import ClazzService

__all__ = ['DeptService', 'EmpService', 'EmpLogService', 'UploadService', 'ClazzService']
