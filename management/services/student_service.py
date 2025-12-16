"""
学生服务层 - 业务唯一入口

职责：业务规则、校验、ORM 访问
禁止：接收 request 对象、返回 Result、做序列化
"""

from datetime import datetime
from ..models import Student


class StudentService:
    
    @staticmethod
    def page(params: dict) -> dict:
        """
        分页条件查询 - 对标 Java StudentServiceImpl.page()
        
        支持条件：name(模糊)、degree、clazzId
        """
        # 1. 提取查询参数
        name = params.get('name')
        degree = params.get('degree')
        clazzId = params.get('clazzId')
        page = int(params.get('page', 1))
        pageSize = int(params.get('pageSize', 10))
        
        # 2. 构建查询条件
        queryset = Student.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        if degree:
            queryset = queryset.filter(degree=int(degree))
        if clazzId:
            queryset = queryset.filter(clazz_id=int(clazzId))
        
        # 3. 排序
        queryset = queryset.order_by('-update_time')
        
        # 4. 分页
        total = queryset.count()
        start = (page - 1) * pageSize
        studentList = queryset[start:start + pageSize]
        
        return {'total': total, 'rows': studentList}
    
    @staticmethod
    def save(data: dict) -> Student:
        """
        添加学生 - 对标 Java StudentServiceImpl.save()
        """
        now = datetime.now()
        return Student.objects.create(
            name=data.get('name'),
            no=data.get('no'),
            gender=data.get('gender'),
            phone=data.get('phone'),
            id_card=data.get('idCard'),
            is_college=StudentService._parse_int(data.get('isCollege')),
            address=data.get('address') or None,
            degree=StudentService._parse_int(data.get('degree')),
            graduation_date=data.get('graduationDate') or None,
            clazz_id=StudentService._parse_int(data.get('clazzId')),
            violation_count=0,
            violation_score=0,
            create_time=now,
            update_time=now
        )
    
    @staticmethod
    def _parse_int(value):
        """将空字符串转为 None，否则转为整数"""
        if value is None or value == '':
            return None
        return int(value)
    
    @staticmethod
    def update(data: dict) -> None:
        """
        修改学生 - 对标 Java StudentServiceImpl.update()
        """
        student_id = data.get('id')
        now = datetime.now()
        Student.objects.filter(pk=student_id).update(
            name=data.get('name'),
            no=data.get('no'),
            gender=data.get('gender'),
            phone=data.get('phone'),
            id_card=data.get('idCard'),
            is_college=StudentService._parse_int(data.get('isCollege')),
            address=data.get('address') or None,
            degree=StudentService._parse_int(data.get('degree')),
            graduation_date=data.get('graduationDate') or None,
            clazz_id=StudentService._parse_int(data.get('clazzId')),
            update_time=now
        )
    
    @staticmethod
    def getInfo(id: int) -> Student:
        """
        根据ID查询学生 - 对标 Java StudentServiceImpl.getInfo()
        """
        return Student.objects.get(pk=id)
    
    @staticmethod
    def delete(ids: list) -> None:
        """
        批量删除学生 - 对标 Java StudentServiceImpl.delete()
        """
        Student.objects.filter(pk__in=ids).delete()
    
    @staticmethod
    def violationHandle(id: int, score: int) -> None:
        """
        违纪处理 - 对标 Java StudentServiceImpl.violationHandle()
        违纪次数 +1，违纪扣分 +score
        """
        from django.db.models import F
        Student.objects.filter(pk=id).update(
            violation_count=F('violation_count') + 1,
            violation_score=F('violation_score') + score,
            update_time=datetime.now()
        )
