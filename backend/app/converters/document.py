from io import BytesIO
from markitdown import MarkItDown
from fastapi import UploadFile

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation"
}

async def extract_text_from_upload(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported file type: {file.content_type}")

    raw_bytes = await file.read()
    if len(raw_bytes) == 0:
        raise ValueError("Uploaded file is empty")

    if len(raw_bytes) > 10 * 1024 * 1024:  # 10MB
        raise ValueError("File too large. Maximum size is 10MB")
    
    buffer = BytesIO(raw_bytes)
    md = MarkItDown()   
    result = md.convert_stream(buffer)
    return result.text_content