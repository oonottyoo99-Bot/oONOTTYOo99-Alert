from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api._shared.scan_logic import scan_group, notify_telegram

router = APIRouter()

# Request body model
class ScanRequest(BaseModel):
    group: str

@router.post("/")
async def scan_endpoint(request: ScanRequest):
    try:
        # เรียกฟังก์ชันสแกนจาก scan_logic.py
        scan_result = scan_group(request.group)

        # ส่งแจ้งเตือนไป Telegram
        notify_telegram(f"Scan result for group '{request.group}': {scan_result}")

        return scan_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

