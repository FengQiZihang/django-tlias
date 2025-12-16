"""
学生序列化器 - 输出结构定义

StudentSerializer: 基础输出
StudentPageSerializer: 分页查询输出（包含 clazzName）
"""

from rest_framework import serializers
from ..models import Student, Clazz


class StudentSerializer(serializers.ModelSerializer):
    """学生基础序列化器"""
    
    class Meta:
        model = Student
        fields = ['id', 'name', 'no', 'gender', 'phone', 'id_card', 'is_college',
                  'address', 'degree', 'graduation_date', 'clazz_id',
                  'violation_count', 'violation_score', 'create_time', 'update_time']


class StudentPageSerializer(serializers.ModelSerializer):
    """
    学生分页查询序列化器 - 包含班级名称
    对标 Java Student 中的 clazzName 字段
    """
    clazzName = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['id', 'name', 'no', 'gender', 'phone', 'id_card', 'is_college',
                  'address', 'degree', 'graduation_date', 'clazz_id', 'clazzName',
                  'violation_count', 'violation_score', 'create_time', 'update_time']
    
    def get_clazzName(self, obj):
        """获取班级名称"""
        if obj.clazz_id:
            try:
                clazz = Clazz.objects.get(pk=obj.clazz_id)
                return clazz.name
            except Clazz.DoesNotExist:
                return None
        return None
