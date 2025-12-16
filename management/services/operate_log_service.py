"""
操作日志服务层 - 业务唯一入口

职责：日志查询
"""

from ..models import OperateLog


class OperateLogService:
    
    @staticmethod
    def page(page: int, pageSize: int) -> dict:
        """
        分页查询操作日志 - 对标 Java OperateLogServiceImpl.page()
        """
        queryset = OperateLog.objects.all().order_by('-operate_time')
        
        # 分页
        total = queryset.count()
        start = (page - 1) * pageSize
        logs = queryset[start:start + pageSize]
        
        # 转换为字典列表（关联查询员工姓名）
        from ..models import Emp
        rows = []
        for log in logs:
            emp_name = None
            if log.operate_emp_id:
                try:
                    emp = Emp.objects.get(pk=log.operate_emp_id)
                    emp_name = emp.name
                except Emp.DoesNotExist:
                    pass
            
            rows.append({
                'id': log.id,
                'operateEmpId': log.operate_emp_id,
                'operateEmpName': emp_name,
                'operateTime': log.operate_time.strftime('%Y-%m-%d %H:%M:%S') if log.operate_time else None,
                'className': log.class_name,
                'methodName': log.method_name,
                'methodParams': log.method_params,
                'returnValue': log.return_value,
                'costTime': log.cost_time
            })
        
        return {'total': total, 'rows': rows}
