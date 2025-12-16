"""
班级模型 - 对标 Java Clazz.java

字段对标：
- name: 班级名称
- room: 班级教室
- begin_date / end_date: 开课/结课时间
- master_id: 班主任（员工ID）
- subject: 学科（1:java, 2:前端, 3:大数据, 4:Python, 5:Go, 6:嵌入式）
- create_time / update_time: 创建/更新时间
"""

from django.db import models


class Clazz(models.Model):
    """班级表"""
    name = models.CharField(max_length=50, verbose_name='班级名称')
    room = models.CharField(max_length=20, null=True, blank=True, verbose_name='班级教室')
    begin_date = models.DateField(null=True, blank=True, verbose_name='开课时间')
    end_date = models.DateField(null=True, blank=True, verbose_name='结课时间')
    master_id = models.IntegerField(null=True, blank=True, verbose_name='班主任ID')
    subject = models.SmallIntegerField(null=True, blank=True, verbose_name='学科')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    update_time = models.DateTimeField(null=True, blank=True, verbose_name='更新时间')

    class Meta:
        db_table = 'clazz'
        managed = False
        verbose_name = '班级'
        verbose_name_plural = '班级'

    def __str__(self):
        return self.name
