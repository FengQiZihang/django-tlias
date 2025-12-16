"""
学生管理路由
"""

from django.urls import path
from ..views.student_views import StudentListView, StudentDetailView, StudentDeleteView, StudentViolationView

urlpatterns = [
    path('students', StudentListView.as_view()),
    path('students/<int:id>', StudentDetailView.as_view()),
    path('students/violation/<int:id>/<int:score>', StudentViolationView.as_view()),
    path('students/<str:ids>', StudentDeleteView.as_view()),
]
