"""
员工实体类

对标 Java: com.example.pojo.Emp
"""

from django.db import models


class Emp(models.Model):
    """员工表"""
    username = models.CharField(max_length=20, unique=True, db_comment='用户名')
    password = models.CharField(max_length=32, null=True, blank=True, db_comment='密码')
    name = models.CharField(max_length=10, db_comment='姓名')
    gender = models.PositiveSmallIntegerField(db_comment='性别, 1:男, 2:女')
    phone = models.CharField(max_length=11, unique=True, db_comment='手机号')
    job = models.PositiveSmallIntegerField(null=True, blank=True, db_comment='职位')
    salary = models.PositiveIntegerField(null=True, blank=True, db_comment='薪资')
    image = models.CharField(max_length=255, null=True, blank=True, db_comment='头像')
    entry_date = models.DateField(null=True, blank=True, db_comment='入职日期')
    dept_id = models.PositiveIntegerField(null=True, blank=True, db_comment='部门ID')  # 逻辑外键
    create_time = models.DateTimeField(null=True, blank=True, db_comment='创建时间')
    update_time = models.DateTimeField(null=True, blank=True, db_comment='修改时间')

    class Meta:
        managed = False
        db_table = 'emp'
        db_table_comment = '员工表'

    def __str__(self):
        return self.name
