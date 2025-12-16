"""
报表统计视图 - 极薄 Controller 层

职责：解析 HTTP 输入 → 调用 Service → 返回统一 Result
"""

import logging
from rest_framework.views import APIView
from ..services.report_service import ReportService
from common.result import Result

logger = logging.getLogger(__name__)


class EmpGenderView(APIView):
    """
    GET /report/empGenderData - 员工性别统计
    """
    
    def get(self, request):
        """员工性别统计"""
        logger.info("员工性别统计")
        data = ReportService.getEmpGenderData()
        return Result.success(data)


class EmpJobView(APIView):
    """
    GET /report/empJobData - 员工职位统计
    """
    
    def get(self, request):
        """员工职位统计"""
        logger.info("员工职位统计")
        data = ReportService.getEmpJobData()
        return Result.success(data)


class StudentDegreeView(APIView):
    """
    GET /report/studentDegreeData - 学生学历统计
    """
    
    def get(self, request):
        """学生学历统计"""
        logger.info("学生学历统计")
        data = ReportService.getStudentDegreeData()
        return Result.success(data)


class StudentCountView(APIView):
    """
    GET /report/studentCountData - 班级人数统计
    """
    
    def get(self, request):
        """班级人数统计"""
        logger.info("班级人数统计")
        data = ReportService.getStudentCountData()
        return Result.success(data)


class OperateLogPageView(APIView):
    """
    GET /log/page - 操作日志分页查询
    """
    
    def get(self, request):
        """操作日志分页查询"""
        page = int(request.query_params.get('page', 1))
        pageSize = int(request.query_params.get('pageSize', 10))
        logger.info(f"日志信息分页查询, page:{page}, pageSize:{pageSize}")
        from ..services.operate_log_service import OperateLogService
        pageResult = OperateLogService.page(page, pageSize)
        return Result.success(pageResult)
