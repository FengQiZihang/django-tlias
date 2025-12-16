"""
学生模型 - 对标 Java Student.java

字段对标：
- name: 姓名
- no: 学号
- gender: 性别 (1:男, 2:女)
- phone: 手机号
- id_card: 身份证号
- is_college: 是否来自院校 (1:是, 0:否)
- address: 联系地址
- degree: 学历 (1:初中, 2:高中, 3:大专, 4:本科, 5:硕士, 6:博士)
- graduation_date: 毕业时间
- clazz_id: 班级ID
- violation_count: 违纪次数
- violation_score: 违纪扣分
- create_time / update_time: 创建/更新时间
"""

from django.db import models


class Student(models.Model):
    """学生表"""
    name = models.CharField(max_length=10, verbose_name='姓名')
    no = models.CharField(max_length=20, unique=True, verbose_name='学号')
    gender = models.SmallIntegerField(null=True, blank=True, verbose_name='性别')
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机号')
    id_card = models.CharField(max_length=18, null=True, blank=True, verbose_name='身份证号')
    is_college = models.SmallIntegerField(null=True, blank=True, verbose_name='是否来自院校')
    address = models.CharField(max_length=200, null=True, blank=True, verbose_name='联系地址')
    degree = models.SmallIntegerField(null=True, blank=True, verbose_name='学历')
    graduation_date = models.DateField(null=True, blank=True, verbose_name='毕业时间')
    clazz_id = models.IntegerField(null=True, blank=True, verbose_name='班级ID')
    violation_count = models.SmallIntegerField(default=0, verbose_name='违纪次数')
    violation_score = models.SmallIntegerField(default=0, verbose_name='违纪扣分')
    create_time = models.DateTimeField(null=True, blank=True, verbose_name='创建时间')
    update_time = models.DateTimeField(null=True, blank=True, verbose_name='更新时间')

    class Meta:
        db_table = 'student'
        managed = False
        verbose_name = '学生'
        verbose_name_plural = '学生'

    def __str__(self):
        return self.name
