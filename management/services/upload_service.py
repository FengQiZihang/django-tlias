"""
文件上传服务层

对标 Java: UploadController.java（本地存储方案）
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from django.conf import settings


class UploadService:
    
    @staticmethod
    def upload(file) -> str:
        """
        上传文件到本地 static/uploads 目录
        返回：可访问的 URL
        """
        # 1. 获取原始文件名和扩展名
        original_name = file.name
        extension = os.path.splitext(original_name)[1]
        
        # 2. 生成新文件名（UUID + 扩展名）- 对标 Java UUID.randomUUID()
        new_filename = f"{uuid.uuid4()}{extension}"
        
        # 3. 创建日期目录（按年/月组织）
        date_path = datetime.now().strftime('%Y/%m')
        upload_dir = Path(settings.MEDIA_ROOT) / date_path
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 4. 保存文件
        file_path = upload_dir / new_filename
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # 5. 返回可访问的 URL
        # 格式：http://localhost:8080/media/2025/12/xxx.png
        return f"{settings.MEDIA_URL}{date_path}/{new_filename}"
