"""
班级管理路由
"""

from django.urls import path
from ..views import ClazzListView
from ..views.clazz_views import ClazzAllView, ClazzDetailView

urlpatterns = [
    path('clazzs', ClazzListView.as_view()),
    path('clazzs/list', ClazzAllView.as_view()),
    path('clazzs/<int:id>', ClazzDetailView.as_view()),
]
