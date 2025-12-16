"""
员工管理路由
"""

from django.urls import path
from ..views import EmpListView, EmpDetailView
from ..views.emp_views import EmpAllView

urlpatterns = [
    path('emps', EmpListView.as_view(), name='emp-list'),
    path('emps/list', EmpAllView.as_view(), name='emp-all'),
    path('emps/<int:id>', EmpDetailView.as_view(), name='emp-detail'),
]
