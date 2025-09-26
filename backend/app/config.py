# app/config.py - Application Configuration
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./test_exam.db"
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    
    # MinIO
    minio_endpoint: str = "http://minio:9000"
    minio_access_key: str = "minio"
    minio_secret_key: str = "minio123"
    minio_bucket_name: str = "smart-exam"
    
    # RabbitMQ
    rabbit_url: str = "amqp://guest:guest@rabbitmq:5672//"
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Application
    app_name: str = "Smart Exam System"
    debug: bool = True
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"

settings = Settings()