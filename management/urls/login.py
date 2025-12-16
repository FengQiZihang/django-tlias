"""
登录路由
"""

from django.urls import path
from ..views.login_views import LoginView

urlpatterns = [
    path('login', LoginView.as_view()),
]
