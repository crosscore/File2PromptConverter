# File2PromptConverter/src/main.py
import mimetypes
import os
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List

app = FastAPI()
app.mount("/", StaticFiles(directory="src/templates", html=True), name="static")

# Get the absolute path to the templates directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(BASE_DIR, "templates")

# Create templates directory if it doesn't exist
os.makedirs(templates_dir, exist_ok=True)

# Jinja2テンプレートの設定
templates = Jinja2Templates(directory=templates_dir)

@app.post("/test_post")
async def test_post():
    return {"message": "POST request received"}

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    """ファイルアップロードフォームを表示する"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """複数のファイルをアップロードし、テキスト化して返す"""
    contents = []
    for file in files:
        content = await file.read()
        decoded_content = decode_content(content, file.filename)
        contents.append(f"--- START OF FILE {file.filename} ---\n{decoded_content}\n--- END OF FILE {file.filename} ---")
    result_text = "\n\n".join(contents)
    return templates.TemplateResponse("result.html", {"request": Request, "result_text": result_text})

def decode_content(content: bytes, filename: str) -> str:
    """ファイルの内容を適切なエンコーディングでデコードする"""
    mime_type, _ = mimetypes.guess_type(filename)

    if mime_type and mime_type.startswith("text"):
        # テキストファイルの場合、文字コードを推定してデコード
        try:
            # 優先的にUTF-8でデコードを試みる
            return content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                # UTF-8でデコードに失敗したら、chardetを使って文字コードを推定
                import chardet
                encoding = chardet.detect(content)["encoding"]
                return content.decode(encoding)
            except (ImportError, UnicodeDecodeError):
                # chardetがない場合や、文字コードの推定に失敗した場合、エラーを返す
                return f"Error: Could not decode file with unknown encoding."
    elif mime_type:
        # バイナリファイルの場合
        return f"Binary file of type: {mime_type}"
    else:
        # MIMEタイプが不明な場合
        return "Error: Unknown file type"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
