"""
学生管理视图 - 极薄 Controller 层

职责：解析 HTTP 输入 → 调用 Service → 返回统一 Result
禁止：直接 ORM 操作、复杂业务逻辑、字段拼装
"""

import logging
from rest_framework.views import APIView
from ..services.student_service import StudentService
from ..serializers.student import StudentPageSerializer
from common.result import Result
from common.log_decorator import log_operation

logger = logging.getLogger(__name__)


class StudentListView(APIView):
    """
    GET /students - 分页查询学生
    POST /students - 添加学生
    PUT /students - 修改学生
    DELETE /students?ids=1,2,3 - 批量删除学生
    """
    
    def get(self, request):
        """分页查询学生"""
        params = {k: v for k, v in request.query_params.items()}
        logger.info(f"分页查询学生：{params}")
        pageResult = StudentService.page(params)
        return Result.success({
            'total': pageResult['total'],
            'rows': StudentPageSerializer(pageResult['rows'], many=True).data
        })
    
    @log_operation
    def post(self, request):
        """添加学生"""
        logger.info(f"添加学生：{request.data}")
        StudentService.save(request.data)
        return Result.success()
    
    @log_operation
    def put(self, request):
        """修改学生"""
        logger.info(f"修改学生：{request.data}")
        StudentService.update(request.data)
        return Result.success()


class StudentDetailView(APIView):
    """
    GET /students/{id} - 根据ID查询学生
    """
    
    def get(self, request, id):
        """根据ID查询学生"""
        logger.info(f"根据ID查询学生：{id}")
        from ..serializers.student import StudentSerializer
        student = StudentService.getInfo(id)
        return Result.success(StudentSerializer(student).data)


class StudentDeleteView(APIView):
    """
    DELETE /students/{ids} - 批量删除学生
    """
    
    @log_operation
    def delete(self, request, ids):
        """批量删除学生"""
        id_list = [int(id) for id in ids.split(',') if id]
        logger.info(f"批量删除学生：{id_list}")
        StudentService.delete(id_list)
        return Result.success()


class StudentViolationView(APIView):
    """
    PUT /students/violation/{id}/{score} - 违纪处理
    """
    
    @log_operation
    def put(self, request, id, score):
        """违纪处理"""
        logger.info(f"违纪处理：学生ID={id}, 扣分={score}")
        StudentService.violationHandle(id, score)
        return Result.success()
