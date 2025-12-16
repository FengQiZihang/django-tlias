"""
操作日志模型 - 对标 Java OperateLog.java

记录增删改操作的日志信息
"""

from django.db import models


class OperateLog(models.Model):
    """操作日志表"""
    operate_emp_id = models.IntegerField(null=True, blank=True, verbose_name='操作人ID')
    operate_time = models.DateTimeField(null=True, blank=True, verbose_name='操作时间')
    class_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='操作的类名')
    method_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='操作的方法名')
    method_params = models.CharField(max_length=2000, null=True, blank=True, verbose_name='方法参数')
    return_value = models.CharField(max_length=2000, null=True, blank=True, verbose_name='返回值')
    cost_time = models.BigIntegerField(null=True, blank=True, verbose_name='方法执行耗时(ms)')

    class Meta:
        db_table = 'operate_log'
        managed = False
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'

    def __str__(self):
        return f"{self.class_name}.{self.method_name}"
