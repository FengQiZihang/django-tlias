"""
员工输出序列化器
"""

from rest_framework import serializers
from ..models import Emp, Dept, EmpExpr


class EmpExprSerializer(serializers.ModelSerializer):
    """工作经历输出 DTO"""
    
    class Meta:
        model = EmpExpr
        fields = ['id', 'begin', 'end', 'company', 'job']


class EmpSerializer(serializers.ModelSerializer):
    """员工列表输出 DTO"""
    
    dept_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Emp
        fields = ['id', 'username', 'name', 'gender', 'phone', 
                  'job', 'salary', 'image', 'entry_date', 
                  'dept_id', 'dept_name', 'create_time', 'update_time']
    
    def get_dept_name(self, obj):
        """逻辑外键查询部门名称 - 对标 Java LEFT JOIN"""
        if obj.dept_id:
            dept = Dept.objects.filter(pk=obj.dept_id).first()
            return dept.name if dept else None
        return None


class EmpDetailSerializer(serializers.ModelSerializer):
    """员工详情输出 DTO - 包含工作经历"""
    
    expr_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Emp
        fields = ['id', 'username', 'name', 'gender', 'phone', 
                  'job', 'salary', 'image', 'entry_date', 
                  'dept_id', 'create_time', 'update_time', 'expr_list']
    
    def get_expr_list(self, obj):
        """获取工作经历列表"""
        expr_list = self.context.get('expr_list', [])
        return EmpExprSerializer(expr_list, many=True).data
