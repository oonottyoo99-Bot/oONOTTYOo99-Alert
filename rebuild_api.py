# rebuild_api.py  — รีเซ็ต /api ให้เหลือ minimal FastAPI 1 ไฟล์สำหรับ Vercel
# ทำให้ /api (root) และ /api/health ใช้งานได้แน่นอน

import json, os, shutil, textwrap

ROOT = os.path.dirname(__file__)
API_DIR = os.path.join(ROOT, "api")

# 1) ลบ api เดิมทั้งโฟลเดอร์ (ถ้ามี)
if os.path.isdir(API_DIR):
    shutil.rmtree(API_DIR)

# 2) สร้างโฟลเดอร์ api ใหม่ (ไม่มี __init__.py!)
os.makedirs(API_DIR, exist_ok=True)

# 3) สร้างไฟล์ api/index.py (ไฟล์เดียวเท่านั้น)
index_py = textwrap.dedent("""
from fastapi import FastAPI

app = FastAPI(title="oONOTTYOo99-Alert API (Minimal)")

@app.get("/")
def root():
    return {
        "ok": True,
        "service": "oONOTTYOo99-Alert API (Minimal)",
        "routes": ["/api", "/api/health"]
    }

@app.get("/health")
def health():
    return {"ok": True}
""").strip() + "\n"

with open(os.path.join(API_DIR, "index.py"), "w", encoding="utf-8") as f:
    f.write(index_py)

# 4) vercel.json — บอกให้ใช้ Python runtime กับทุกไฟล์ใน api/**/*.py
vercel_json = {
    "functions": {
        "api/**/*.py": {
            "runtime": "python3.12"
        }
    }
}
with open(os.path.join(ROOT, "vercel.json"), "w", encoding="utf-8") as f:
    json.dump(vercel_json, f, indent=2)

print("✅ Rebuilt minimal /api for Vercel:")
print(" - api/index.py")
print(" - vercel.json (python3.12)")
print("\nถัดไปให้ commit/push แล้วทดสอบ /api และ /api/health ครับ")
