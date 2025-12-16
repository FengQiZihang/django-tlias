"""
部门服务层 - 业务唯一入口

职责：业务规则、校验、ORM 访问
禁止：接收 request 对象、返回 Result、做序列化
"""

from datetime import datetime
from ..models import Dept


class DeptService:
    
    @staticmethod
    def findAll():
        """查询所有部门"""
        return Dept.objects.all().order_by('-update_time')
    
    @staticmethod
    def getById(id: int) -> Dept:
        """根据ID查询部门"""
        return Dept.objects.get(pk=id)
    
    @staticmethod
    def add(data: dict) -> Dept:
        """新增部门"""
        name = data.get('name')
        now = datetime.now()
        return Dept.objects.create(name=name, create_time=now, update_time=now)
    
    @staticmethod
    def update(data: dict) -> Dept:
        """修改部门"""
        id = data.get('id')
        name = data.get('name')
        dept = Dept.objects.get(pk=id)
        dept.name = name
        dept.update_time = datetime.now()
        dept.save()
        return dept
    
    @staticmethod
    def deleteById(id: int) -> None:
        """
        删除部门 - 对标 Java DeptServiceImpl.deleteById()
        
        业务规则：部门下有员工时不能删除
        """
        from common.exceptions import BusinessException
        from ..models import Emp
        
        # 1. 判断部门下是否有员工
        count = Emp.objects.filter(dept_id=id).count()
        if count > 0:
            raise BusinessException("部门下有员工，不能删除")
        
        # 2. 删除部门
        Dept.objects.filter(pk=id).delete()
