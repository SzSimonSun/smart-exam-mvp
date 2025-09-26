"""
MinIO客户端配置
"""
import os
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class MinIOClient:
    def __init__(self):
        # MinIO配置 - 可以通过环境变量配置
        self.endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
        self.secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
        self.secure = os.getenv('MINIO_SECURE', 'false').lower() == 'true'
        self.bucket_name = os.getenv('MINIO_BUCKET', 'exam-pdfs')
        
        self.client = None
        self.available = False
        
        try:
            # 创建MinIO客户端
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            
            # 确保bucket存在
            self._ensure_bucket_exists()
            self.available = True
            logger.info("MinIO client initialized successfully")
        except Exception as e:
            logger.warning(f"MinIO client initialization failed: {e}")
            self.available = False
    
    def _ensure_bucket_exists(self):
        """确保bucket存在"""
        if not self.client:
            return
            
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.info(f"Bucket {self.bucket_name} already exists")
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise
    
    def upload_file(self, file_path: str, object_name: str, content_type: str = 'application/pdf'):
        """
        上传文件到MinIO
        
        Args:
            file_path: 本地文件路径
            object_name: MinIO中的对象名称
            content_type: 文件类型
            
        Returns:
            object_name: 上传成功的对象名称
        """
        if not self.available or not self.client:
            raise Exception("MinIO client is not available")
            
        try:
            self.client.fput_object(
                self.bucket_name,
                object_name,
                file_path,
                content_type=content_type
            )
            logger.info(f"File uploaded successfully: {object_name}")
            return object_name
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise
    
    def get_presigned_url(self, object_name: str, expires_seconds: int = 3600):
        """
        获取预签名URL用于下载
        
        Args:
            object_name: MinIO中的对象名称
            expires_seconds: URL过期时间（秒）
            
        Returns:
            presigned_url: 预签名URL
        """
        if not self.available or not self.client:
            raise Exception("MinIO client is not available")
            
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires_seconds)
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def get_public_url(self, object_name: str):
        """
        获取公共访问URL（如果bucket是公共的）
        
        Args:
            object_name: MinIO中的对象名称
            
        Returns:
            public_url: 公共访问URL
        """
        protocol = 'https' if self.secure else 'http'
        base_url = f"{protocol}://{self.endpoint}"
        return f"{base_url}/{self.bucket_name}/{object_name}"

# 全局MinIO客户端实例
minio_client = MinIOClient()