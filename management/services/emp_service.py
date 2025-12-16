"""
员工服务层 - 业务唯一入口

职责：业务规则、校验、ORM 访问
禁止：接收 request 对象、返回 Result、做序列化
"""

import hashlib
from datetime import datetime
from django.db import transaction
from ..models import Emp, EmpExpr
from .emp_log_service import EmpLogService


class EmpService:
    
    @staticmethod
    def page(params: dict) -> dict:
        """
        分页条件查询 - 对标 Java PageHelper + 动态 SQL
        """
        # 1. 提取查询参数
        name = params.get('name')
        gender = params.get('gender')
        begin = params.get('begin')
        end = params.get('end')
        page = int(params.get('page', 1))
        pageSize = int(params.get('pageSize', 10))
        
        # 2. 构建查询条件（对标动态 SQL）
        queryset = Emp.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        if gender:
            queryset = queryset.filter(gender=int(gender))
        if begin and end:
            queryset = queryset.filter(entry_date__range=[begin, end])
        
        # 3. 排序
        queryset = queryset.order_by('-update_time')
        
        # 4. 分页（对标 PageHelper）
        total = queryset.count()
        start = (page - 1) * pageSize
        empList = queryset[start:start + pageSize]
        
        return {'total': total, 'rows': empList}
    
    @staticmethod
    def findAll():
        """
        查询所有员工 - 对标 Java EmpServiceImpl.findAll()
        """
        return Emp.objects.all().order_by('-update_time')
    
    @staticmethod
    @transaction.atomic  # 对标 @Transactional(rollbackFor = Exception.class)
    def save(data: dict) -> Emp:
        """
        新增员工 - 对标 Java EmpServiceImpl.save()
        包含：基本信息、工作经历、操作日志
        """
        try:
            # 1. 补全基础字段，密码 MD5 加密
            password = hashlib.md5('123456'.encode()).hexdigest()
            now = datetime.now()
            
            emp = Emp.objects.create(
                username=data.get('username'),
                password=password,
                name=data.get('name'),
                gender=data.get('gender'),
                phone=data.get('phone'),
                job=EmpService._parse_int(data.get('job')),
                salary=EmpService._parse_int(data.get('salary')),
                image=data.get('image') or None,
                entry_date=data.get('entryDate') or None,
                dept_id=EmpService._parse_int(data.get('deptId')),
                create_time=now,
                update_time=now
            )
            
            # 2. 保存工作经历（批量），过滤掉空记录
            exprList = data.get('exprList', [])
            if exprList:
                # 过滤掉没有填写公司名称的空记录
                valid_exprs = [
                    EmpExpr(
                        emp_id=emp.id,
                        begin=expr.get('begin') or None,
                        end=expr.get('end') or None,
                        company=expr.get('company') or None,
                        job=expr.get('job') or None
                    )
                    for expr in exprList
                    if expr.get('company')  # 只保存有公司名称的记录
                ]
                if valid_exprs:
                    EmpExpr.objects.bulk_create(valid_exprs)
            
            return emp
        finally:
            # 3. 记录操作日志（finally 确保日志记录）
            EmpLogService.insertLog(f"新增员工：{data.get('name')}")
    
    @staticmethod
    def _parse_int(value):
        """将空字符串转为 None，否则转为整数"""
        if value is None or value == '':
            return None
        return int(value)
    
    @staticmethod
    @transaction.atomic  # 对标 @Transactional(rollbackFor = Exception.class)
    def delete(ids: list) -> None:
        """
        批量删除员工 - 对标 Java EmpServiceImpl.delete()
        包含：员工基本信息、工作经历
        """
        # 1. 批量删除员工基本信息
        Emp.objects.filter(pk__in=ids).delete()
        # 2. 批量删除员工工作经历信息
        EmpExpr.objects.filter(emp_id__in=ids).delete()
    
    @staticmethod
    def getInfo(id: int) -> dict:
        """
        根据ID查询员工详情 - 对标 Java EmpServiceImpl.getInfo()
        返回：员工基本信息 + 工作经历列表
        """
        emp = Emp.objects.get(pk=id)
        exprList = EmpExpr.objects.filter(emp_id=id)
        return {'emp': emp, 'exprList': exprList}
    
    @staticmethod
    @transaction.atomic  # 对标 @Transactional(rollbackFor = Exception.class)
    def update(data: dict) -> None:
        """
        更新员工信息 - 对标 Java EmpServiceImpl.update()
        包含：员工基本信息、工作经历（先删后增）
        """
        emp_id = data.get('id')
        now = datetime.now()
        
        # 1. 更新员工基本信息
        Emp.objects.filter(pk=emp_id).update(
            username=data.get('username'),
            name=data.get('name'),
            gender=data.get('gender'),
            phone=data.get('phone'),
            job=EmpService._parse_int(data.get('job')),
            salary=EmpService._parse_int(data.get('salary')),
            image=data.get('image') or None,
            entry_date=data.get('entryDate') or None,
            dept_id=EmpService._parse_int(data.get('deptId')),
            update_time=now
        )
        
        # 2. 更新工作经历（先删后增）
        # 2.1 删除旧的工作经历
        EmpExpr.objects.filter(emp_id=emp_id).delete()
        
        # 2.2 插入新的工作经历，过滤空记录
        exprList = data.get('exprList', [])
        if exprList:
            valid_exprs = [
                EmpExpr(
                    emp_id=emp_id,
                    begin=expr.get('begin') or None,
                    end=expr.get('end') or None,
                    company=expr.get('company') or None,
                    job=expr.get('job') or None
                )
                for expr in exprList
                if expr.get('company')  # 只保存有公司名称的记录
            ]
            if valid_exprs:
                EmpExpr.objects.bulk_create(valid_exprs)
    
    @staticmethod
    def login(username: str, password: str) -> dict:
        """
        员工登录 - 对标 Java EmpServiceImpl.login()
        
        Returns:
            成功返回 {id, username, name, token}，失败返回 None
        """
        from common.jwt_utils import generate_jwt
        
        # 1. 密码 MD5 加密
        password_md5 = hashlib.md5(password.encode()).hexdigest()
        
        # 2. 根据用户名和密码查询员工
        try:
            emp = Emp.objects.get(username=username, password=password_md5)
        except Emp.DoesNotExist:
            return None
        
        # 3. 生成 JWT Token
        token = generate_jwt({
            'id': emp.id,
            'username': emp.username
        })
        
        # 4. 返回登录信息
        return {
            'id': emp.id,
            'username': emp.username,
            'name': emp.name,
            'token': token
        }
