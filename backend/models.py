from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Pydantic模型（用于API响应）
class FruitDetection(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    
class DetectionResult(BaseModel):
    id: str
    filename: str
    detections: List[FruitDetection]
    result_image_url: str
    timestamp: datetime

class User(BaseModel):
    id: str
    username: str
    email: str

# SQLAlchemy模型（用于数据库）
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    detection_history = relationship("DetectionHistory", back_populates="user")

class DetectionHistory(Base):
    __tablename__ = "detection_history"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    filename = Column(String)
    result_data = Column(Text)  # JSON格式的检测结果
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("UserDB", back_populates="detection_history")