"""
员工工作经历实体类

对标 Java: com.example.pojo.EmpExpr
"""

from django.db import models


class EmpExpr(models.Model):
    """员工工作经历表"""
    emp_id = models.PositiveIntegerField(db_comment='员工ID')  # 逻辑外键
    begin = models.DateField(null=True, blank=True, db_comment='开始时间')
    end = models.DateField(null=True, blank=True, db_comment='结束时间')
    company = models.CharField(max_length=50, null=True, blank=True, db_comment='公司名称')
    job = models.CharField(max_length=50, null=True, blank=True, db_comment='职位')

    class Meta:
        managed = False
        db_table = 'emp_expr'
        db_table_comment = '员工工作经历'

    def __str__(self):
        return f"{self.company} - {self.job}"
