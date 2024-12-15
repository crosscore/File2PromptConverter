# src/main.py

import mimetypes
import os
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ベースディレクトリとテンプレートディレクトリの設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")
static_dir = os.path.join(BASE_DIR, "static")

# ディレクトリが存在しない場合は作成
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Jinja2テンプレートの設定
templates = Jinja2Templates(directory=templates_dir)

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    """ファイルアップロードフォームを表示する"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=PlainTextResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """複数のファイルをアップロードし、テキスト化して返す"""
    try:
        contents = []
        for file in files:
            content = await file.read()
            decoded_content = decode_content(content, file.filename)
            contents.append(f"--- START OF FILE {file.filename} ---\n{decoded_content}\n--- END OF FILE {file.filename} ---")
        result_text = "\n\n".join(contents)
        return PlainTextResponse(result_text)
    except Exception as e:
        return PlainTextResponse(f"Error processing files: {str(e)}", status_code=500)

def decode_content(content: bytes, filename: str) -> str:
    """ファイルの内容を適切なエンコーディングでデコードする"""
    mime_type, _ = mimetypes.guess_type(filename)

    if mime_type and mime_type.startswith("text"):
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                import chardet
                encoding = chardet.detect(content)["encoding"]
                return content.decode(encoding or 'utf-8')
            except (ImportError, UnicodeDecodeError):
                return f"Error: Could not decode file with unknown encoding."
    elif mime_type:
        return f"Binary file of type: {mime_type}"
    else:
        return "Error: Unknown file type"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
