from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
import uuid
from datetime import datetime
from typing import List
import json

from models import DetectionResult, User, DetectionHistory
from database import engine, SessionLocal, Base
from auth import get_current_user
from detection_service import FruitDetectionService

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="水果成熟度检测系统", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建检测服务实例
detection_service = FruitDetectionService()

# 静态文件目录
UPLOAD_DIR = "uploads"
RESULTS_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")

@app.get("/")
async def root():
    return {"message": "水果成熟度检测系统 API", "version": "1.0.0"}

@app.post("/api/detect", response_model=DetectionResult)
async def detect_fruit(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """检测水果成熟度"""
    
    # 验证文件类型
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="请上传图片文件")
    
    # 生成唯一文件名
    file_extension = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 保存上传的文件
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # 进行水果检测
        detection_result = await detection_service.detect_fruit(file_path)
        
        # 保存检测结果
        result_id = str(uuid.uuid4())
        result_data = {
            "id": result_id,
            "filename": filename,
            "original_path": file_path,
            "result_path": detection_result.result_path,
            "detections": [detection.dict() for detection in detection_result.detections],
            "timestamp": datetime.now().isoformat(),
            "user_id": current_user.id
        }
        
        # 保存到数据库
        db = SessionLocal()
        try:
            history = DetectionHistory(
                id=result_id,
                user_id=current_user.id,
                filename=filename,
                result_data=json.dumps(result_data),
                created_at=datetime.now()
            )
            db.add(history)
            db.commit()
        finally:
            db.close()
        
        return DetectionResult(
            id=result_id,
            filename=filename,
            detections=detection_result.detections,
            result_image_url=f"/results/{os.path.basename(detection_result.result_path)}",
            timestamp=datetime.now()
        )
        
    except Exception as e:
        # 删除上传的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@app.get("/api/history", response_model=List[DetectionHistory])
async def get_detection_history(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """获取检测历史"""
    db = SessionLocal()
    try:
        history = db.query(DetectionHistory).filter(
            DetectionHistory.user_id == current_user.id
        ).order_by(DetectionHistory.created_at.desc()).offset(skip).limit(limit).all()
        return history
    finally:
        db.close()

@app.get("/api/history/{history_id}")
async def get_detection_details(history_id: str, current_user: User = Depends(get_current_user)):
    """获取特定检测记录的详细信息"""
    db = SessionLocal()
    try:
        history = db.query(DetectionHistory).filter(
            DetectionHistory.id == history_id,
            DetectionHistory.user_id == current_user.id
        ).first()
        
        if not history:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        return json.loads(history.result_data)
    finally:
        db.close()

@app.get("/api/stats")
async def get_statistics(current_user: User = Depends(get_current_user)):
    """获取用户统计信息"""
    db = SessionLocal()
    try:
        total_detections = db.query(DetectionHistory).filter(
            DetectionHistory.user_id == current_user.id
        ).count()
        
        # 获取最近7天的检测统计
        seven_days_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_detections = db.query(DetectionHistory).filter(
            DetectionHistory.user_id == current_user.id,
            DetectionHistory.created_at >= seven_days_ago
        ).count()
        
        return {
            "total_detections": total_detections,
            "recent_detections": recent_detections
        }
    finally:
        db.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)