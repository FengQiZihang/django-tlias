"""
数据模型模块
"""

from .dept import Dept
from .emp import Emp
from .emp_expr import EmpExpr
from .emp_log import EmpLog
from .clazz import Clazz
from .student import Student
from .operate_log import OperateLog

__all__ = ['Dept', 'Emp', 'EmpExpr', 'EmpLog', 'Clazz', 'Student', 'OperateLog']
