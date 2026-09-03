from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

from app.config import settings


def validate_and_save_upload(file: UploadFile) -> tuple[str, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail='No file selected.')

    suffix = Path(file.filename).suffix.lower()
    allowed = {'.pdf', '.docx'}
    if suffix not in allowed:
        raise HTTPException(status_code=400, detail='Unsupported file type.')

    content = file.file.read() if file.file else b''
    if not content:
        raise HTTPException(status_code=400, detail='Uploaded file is empty.')

    max_size = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail='File exceeds the allowed size.')

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid4()}{suffix}"
    save_path = upload_dir / safe_name
    save_path.write_bytes(content)
    return str(save_path), suffix.lstrip('.')
