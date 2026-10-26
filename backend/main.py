import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
ORIGINAL_DIR = "uploads/original"
THUMB_DIR = "uploads/thumbs"
ALLOWED_TYPES = ["image/png", "image/jpeg"]
MAX_FILE_SIZE = 5 * 1024 * 1024

os.makedirs(ORIGINAL_DIR, exist_ok=True)
os.makedirs(THUMB_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def home():
    return {"message": "Сервер работает"}


@app.post("/upload-image/")
async def upload_image(request: Request, file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый тип файла: {file.content_type}. Можно только PNG или JPEG",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл слишком большой (максимум 5 МБ)")

    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1].lower()
    original_path = f"{ORIGINAL_DIR}/{file_id}.{extension}"
    thumb_path = f"{THUMB_DIR}/{file_id}_thumb.{extension}"

    with open(original_path, "wb") as f:
        f.write(contents)

    try:
        img = Image.open(original_path)
        width, height = img.size
        img.thumbnail((200, 200))
        img.save(thumb_path)
    except Exception:
        os.remove(original_path)
        raise HTTPException(status_code=400, detail="Не получилось открыть файл как изображение")

    base_url = str(request.base_url)

    return {
        "original_url": f"{base_url}uploads/original/{file_id}.{extension}",
        "thumbnail_url": f"{base_url}uploads/thumbs/{file_id}_thumb.{extension}",
        "width": width,
        "height": height,
    }
