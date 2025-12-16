"""
视图模块
"""

from .dept_views import DeptListView, DeptDetailView
from .emp_views import EmpListView, EmpDetailView
from .upload_views import UploadView
from .clazz_views import ClazzListView

__all__ = ['DeptListView', 'DeptDetailView', 'EmpListView', 'EmpDetailView', 'UploadView',
           'ClazzListView']
