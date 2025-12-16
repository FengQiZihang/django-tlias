"""
员工操作日志实体类

对标 Java: com.example.pojo.EmpLog
"""

from django.db import models


class EmpLog(models.Model):
    """员工操作日志表"""
    operate_time = models.DateTimeField(null=True, blank=True, db_comment='操作时间')
    info = models.CharField(max_length=2000, null=True, blank=True, db_comment='日志信息')

    class Meta:
        managed = False
        db_table = 'emp_log'
        db_table_comment = '员工日志表'

    def __str__(self):
        return f"{self.operate_time} - {self.info[:50]}"
