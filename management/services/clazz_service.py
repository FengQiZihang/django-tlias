"""
班级服务层 - 业务唯一入口

职责：业务规则、校验、ORM 访问
禁止：接收 request 对象、返回 Result、做序列化
"""

from datetime import datetime
from ..models import Clazz


class ClazzService:
    
    @staticmethod
    def page(params: dict) -> dict:
        """
        分页条件查询 - 对标 Java ClazzServiceImpl.page()
        
        支持条件：name(模糊)、begin、end(结课时间范围)
        """
        # 1. 提取查询参数
        name = params.get('name')
        begin = params.get('begin')
        end = params.get('end')
        page = int(params.get('page', 1))
        pageSize = int(params.get('pageSize', 10))
        
        # 2. 构建查询条件
        queryset = Clazz.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        if begin and end:
            # 按结课时间范围筛选
            queryset = queryset.filter(end_date__range=[begin, end])
        
        # 3. 排序
        queryset = queryset.order_by('-update_time')
        
        # 4. 分页
        total = queryset.count()
        start = (page - 1) * pageSize
        clazzList = queryset[start:start + pageSize]
        
        return {'total': total, 'rows': clazzList}
    
    @staticmethod
    def findAll():
        """
        查询所有班级 - 对标 Java ClazzServiceImpl.findAll()
        """
        return Clazz.objects.all().order_by('-update_time')
    
    @staticmethod
    def save(data: dict) -> Clazz:
        """
        添加班级 - 对标 Java ClazzServiceImpl.save()
        """
        now = datetime.now()
        return Clazz.objects.create(
            name=data.get('name'),
            room=data.get('room') or None,
            begin_date=data.get('beginDate'),
            end_date=data.get('endDate'),
            master_id=ClazzService._parse_int(data.get('masterId')),
            subject=data.get('subject'),
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
    def getInfo(id: int) -> Clazz:
        """
        根据ID查询班级 - 对标 Java ClazzServiceImpl.getInfo()
        """
        return Clazz.objects.get(pk=id)
    
    @staticmethod
    def update(data: dict) -> None:
        """
        修改班级 - 对标 Java ClazzServiceImpl.update()
        """
        clazz_id = data.get('id')
        now = datetime.now()
        Clazz.objects.filter(pk=clazz_id).update(
            name=data.get('name'),
            room=data.get('room') or None,
            begin_date=data.get('beginDate'),
            end_date=data.get('endDate'),
            master_id=ClazzService._parse_int(data.get('masterId')),
            subject=data.get('subject'),
            update_time=now
        )
    
    @staticmethod
    def delete(id: int) -> None:
        """
        删除班级 - 对标 Java ClazzServiceImpl.delete()
        """
        Clazz.objects.filter(pk=id).delete()
