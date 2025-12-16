"""
报表统计服务层 - 业务唯一入口

职责：数据统计、聚合查询
"""

from django.db.models import Count, Case, When, CharField, Value
from ..models import Emp, Student, Clazz


class ReportService:
    
    # 职位映射
    JOB_MAP = {
        1: '班主任',
        2: '讲师',
        3: '学工主管',
        4: '教研主管',
        5: '咨询师'
    }
    
    # 学历映射
    DEGREE_MAP = {
        1: '初中',
        2: '高中',
        3: '大专',
        4: '本科',
        5: '硕士',
        6: '博士'
    }
    
    @staticmethod
    def getEmpGenderData() -> list:
        """
        员工性别统计 - 对标 Java ReportServiceImpl.getEmpGenderData()
        返回格式：[{"name": "男", "value": 10}, {"name": "女", "value": 5}]
        """
        result = Emp.objects.values('gender').annotate(value=Count('id'))
        gender_data = []
        for item in result:
            gender_data.append({
                'name': '男' if item['gender'] == 1 else '女',
                'value': item['value']
            })
        return gender_data
    
    @staticmethod
    def getEmpJobData() -> dict:
        """
        员工职位统计 - 对标 Java ReportServiceImpl.getEmpJobData()
        返回格式：{"jobList": ["班主任", "讲师", ...], "dataList": [10, 20, ...]}
        """
        result = Emp.objects.exclude(job__isnull=True).values('job').annotate(emp_count=Count('id'))
        jobList = []
        dataList = []
        for item in result:
            job_name = ReportService.JOB_MAP.get(item['job'], '其他')
            jobList.append(job_name)
            dataList.append(item['emp_count'])
        return {'jobList': jobList, 'dataList': dataList}
    
    @staticmethod
    def getStudentDegreeData() -> list:
        """
        学生学历统计 - 对标 Java ReportServiceImpl.getStudentDegreeData()
        返回格式：[{"name": "本科", "value": 10}, ...]
        """
        result = Student.objects.exclude(degree__isnull=True).values('degree').annotate(value=Count('id'))
        degree_data = []
        for item in result:
            degree_name = ReportService.DEGREE_MAP.get(item['degree'], '其他')
            degree_data.append({
                'name': degree_name,
                'value': item['value']
            })
        return degree_data
    
    @staticmethod
    def getStudentCountData() -> dict:
        """
        班级学生人数统计 - 对标 Java ReportServiceImpl.getStudentCountData()
        返回格式：{"clazzList": ["Java班", "前端班", ...], "dataList": [30, 25, ...]}
        """
        # 统计每个班级的学生数量
        result = Student.objects.exclude(clazz_id__isnull=True).values('clazz_id').annotate(
            student_count=Count('id')
        )
        clazzList = []
        dataList = []
        # 获取班级名称
        for item in result:
            try:
                clazz = Clazz.objects.get(pk=item['clazz_id'])
                clazzList.append(clazz.name)
                dataList.append(item['student_count'])
            except Clazz.DoesNotExist:
                pass
        return {'clazzList': clazzList, 'dataList': dataList}
