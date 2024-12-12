import io
import mimetypes
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from typing import List

app = FastAPI()

# Jinja2テンプレートの設定
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    """ファイルアップロードフォームを表示する"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_files(request: Request, files: List[UploadFile] = File(...)):
    """複数のファイルをアップロードし、テキスト化して返す"""
    contents = []
    for file in files:
        content = await file.read()
        decoded_content = decode_content(content, file.filename)
        contents.append(f"```{file.filename}\n{decoded_content}\n```")
    result_text = "\n".join(contents)
    return templates.TemplateResponse("result.html", {"request": request, "result_text": result_text})

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
                # chardetがない場合や、文字コードの推定に失敗した場合は、エラーメッセージを返す
                return f"Error: Could not decode file with unknown encoding."
    elif mime_type:
        # バイナリファイルの場合
        return f"Binary file of type: {mime_type}"
    else:
        # MIMEタイプが不明な場合
        return "Error: Unknown file type"
