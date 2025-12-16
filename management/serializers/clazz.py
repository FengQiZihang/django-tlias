"""
班级序列化器 - 输出结构定义

ClazzSerializer: 基础输出（分页列表用）
ClazzPageSerializer: 分页查询输出（包含 masterName、status）
"""

from datetime import date
from rest_framework import serializers
from ..models import Clazz, Emp


class ClazzSerializer(serializers.ModelSerializer):
    """班级基础序列化器"""
    
    class Meta:
        model = Clazz
        fields = ['id', 'name', 'room', 'begin_date', 'end_date', 
                  'master_id', 'subject', 'create_time', 'update_time']


class ClazzPageSerializer(serializers.ModelSerializer):
    """
    班级分页查询序列化器 - 包含班主任姓名和状态
    对标 Java Clazz 中的 masterName、status 字段
    """
    masterName = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Clazz
        fields = ['id', 'name', 'room', 'begin_date', 'end_date', 
                  'master_id', 'masterName', 'create_time', 'update_time', 'status']
    
    def get_masterName(self, obj):
        """获取班主任姓名"""
        if obj.master_id:
            try:
                emp = Emp.objects.get(pk=obj.master_id)
                return emp.name
            except Emp.DoesNotExist:
                return None
        return None
    
    def get_status(self, obj):
        """
        计算班级状态 - 对标 Java 逻辑
        未开班: 当前日期 < 开课日期
        已开班: 开课日期 <= 当前日期 <= 结课日期
        已结课: 当前日期 > 结课日期
        """
        today = date.today()
        if obj.begin_date and today < obj.begin_date:
            return "未开班"
        elif obj.end_date and today > obj.end_date:
            return "已结课"
        else:
            return "已开班"
