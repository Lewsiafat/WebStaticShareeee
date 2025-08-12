from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import uuid
import aiofiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# 儲存上傳檔案的目錄
UPLOAD_DIR = "static_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 儲存已上傳資源的元數據 (簡單起見，這裡使用字典，實際生產環境建議使用資料庫)
# 格式: { "id": {"filename": "xxx.html", "url": "/static/xxx.html", "type": "file/paste"} }
uploaded_resources = {}

# 掛載靜態檔案目錄，讓 FastAPI 可以直接提供這些檔案
# /resources/{resource_id} 會對應到 UPLOAD_DIR/{resource_id}
app.mount("/resources", StaticFiles(directory=UPLOAD_DIR), name="resources")

class PasteContent(BaseModel):
    content: str
    file_extension: str = "html" # 預設為 HTML

# --- API 端點 ---

@app.get("/")
async def read_root():
    return {"message": "歡迎來到靜態網頁服務後端！"}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    """上傳單一檔案。"""
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")

    try:
        async with aiofiles.open(save_path, "wb") as out_file:
            while content := await file.read(1024):  # 分塊讀取寫入
                await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上傳檔案失敗: {e}")

    resource_url = f"/resources/{file_id}{file_extension}"
    uploaded_resources[file_id] = {
        "filename": file.filename,
        "id": file_id,
        "url": resource_url,
        "type": "file",
        "original_name": file.filename,
        "extension": file_extension
    }
    return {"message": "檔案上傳成功", "url": resource_url, "id": file_id}

@app.post("/pastecontent/")
async def paste_content(item: PasteContent):
    """貼上內容並儲存為檔案。"""
    file_id = str(uuid.uuid4())
    file_extension = item.file_extension if item.file_extension.startswith('.') else f".{item.file_extension}"
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_extension}")

    try:
        async with aiofiles.open(save_path, "w", encoding="utf-8") as out_file:
            await out_file.write(item.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"儲存內容失敗: {e}")

    resource_url = f"/resources/{file_id}{file_extension}"
    uploaded_resources[file_id] = {
        "filename": f"pasted_content{file_extension}",
        "id": file_id,
        "url": resource_url,
        "type": "paste",
        "extension": file_extension
    }
    return {"message": "內容儲存成功", "url": resource_url, "id": file_id}

@app.get("/list/")
async def list_resources():
    """獲取所有已上傳資源的列表。"""
    # 這裡返回的資料結構可以根據前端需求進行調整
    return {"resources": list(uploaded_resources.values())}

# 可選: 直接重定向到上傳的資源
@app.get("/go/{resource_id}")
async def go_to_resource(resource_id: str):
    """根據 ID 重定向到對應的資源 URL。"""
    if resource_id in uploaded_resources:
        return RedirectResponse(url=uploaded_resources[resource_id]["url"])
    raise HTTPException(status_code=404, detail="資源未找到")
