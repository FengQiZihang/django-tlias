"""
部门输出序列化器

全局驼峰渲染器会自动将 create_time -> createTime
"""

from rest_framework import serializers
from ..models import Dept


class DeptSerializer(serializers.ModelSerializer):
    """部门输出 DTO"""
    
    class Meta:
        model = Dept
        fields = ['id', 'name', 'create_time', 'update_time']
