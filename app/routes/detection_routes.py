from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.detection.hijab_detector import detect_hijabs
import shutil
import os
import uuid

router = APIRouter(prefix="/detect", tags=["Hijab Detection"])

UPLOAD_DIR = "uploads"

@router.post("/")
async def detect_image(file: UploadFile = File(...)):
    try:
        # Save uploaded image
        file_ext = os.path.splitext(file.filename)[1]
        file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{file_ext}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run detection
        count = detect_hijabs(file_path)

        return JSONResponse(
            content={
                "message": f"🧕 {count} hijab wearers detected",
                "count": count
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
