"""
部门实体类

对标 Java: com.example.pojo.Dept
"""

from django.db import models


class Dept(models.Model):
    """部门表"""
    name = models.CharField(unique=True, max_length=10, db_comment='部门名称')
    create_time = models.DateTimeField(blank=True, null=True, db_comment='创建时间')
    update_time = models.DateTimeField(blank=True, null=True, db_comment='修改时间')

    class Meta:
        managed = False  # 不让 Django 管理此表的创建/删除
        db_table = 'dept'
        db_table_comment = '部门表'

    def __str__(self):
        return self.name
