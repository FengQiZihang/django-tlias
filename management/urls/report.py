"""
报表统计路由
"""

from django.urls import path
from ..views.report_views import EmpGenderView, EmpJobView, StudentDegreeView, StudentCountView, OperateLogPageView

urlpatterns = [
    path('report/empGenderData', EmpGenderView.as_view()),
    path('report/empJobData', EmpJobView.as_view()),
    path('report/studentDegreeData', StudentDegreeView.as_view()),
    path('report/studentCountData', StudentCountView.as_view()),
    path('log/page', OperateLogPageView.as_view()),
]
