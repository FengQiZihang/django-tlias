"""
部门管理路由
"""

from django.urls import path
from ..views import DeptListView, DeptDetailView

urlpatterns = [
    path('depts', DeptListView.as_view(), name='dept-list'),
    path('depts/<int:id>', DeptDetailView.as_view(), name='dept-detail'),
]
