"""
员工日志服务层

对标 Java: EmpLogServiceImpl
独立事务记录日志，不影响主业务
"""

from datetime import datetime
from ..models import EmpLog


class EmpLogService:
    
    @staticmethod
    def insertLog(info: str):
        """
        记录操作日志 - 对标 Java @Transactional(propagation=REQUIRES_NEW)
        独立保存，日志失败不影响主业务
        """
        EmpLog.objects.create(
            operate_time=datetime.now(),
            info=info
        )
