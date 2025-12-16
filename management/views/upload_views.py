"""
文件上传视图

对标 Java: UploadController.java
"""

import logging
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from ..services import UploadService
from common.result import Result

logger = logging.getLogger(__name__)


class UploadView(APIView):
    """
    POST /upload - 上传文件
    """
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        """上传文件"""
        file = request.FILES.get('file')
        if not file:
            return Result.error("请选择要上传的文件")
        
        logger.info(f"文件原始名:{file.name}, 文件大小:{file.size}")
        url = UploadService.upload(file)
        logger.info(f"文件上传成功, url:{url}")
        return Result.success(url)
