from fastapi import FastAPI, APIRouter, Depends, UploadFile ,status
from fastapi.responses import JSONResponse
import os
from helper.config import get_settings, Settings
from controllers import DataController , ProjectController , ProcessController
import aiofiles
from models import ResponseSignals
import logging
from .schemes.data import ProcessRequest


logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
    )

@data_router.post("/upload/{project_id}")
async def upload_file(
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    is_valid, message = DataController().validate_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Signal": message}
        )

    data_controller = DataController()

    new_filename, random_file_name, _, clean_filename = (
        data_controller.generate_unique_filepath(
            original_filename=file.filename,
            project_id=project_id
        )
    )

    project_dir_path = ProjectController().get_project_file(
        project_id=project_id
    )

    file_path = os.path.join(project_dir_path, new_filename)
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while content := await file.read(
                app_settings.FILE_DEFAULT_CHUNK_SIZE
            ):
                await f.write(content)
    except Exception as e:
        logger.error(f"Error occurred while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Signal": ResponseSignals.FILE_UPLOAD_FAILED.value, "error": str(e)}
        )

    return JSONResponse(
        content={
            "Signal": ResponseSignals.FILE_UPLOAD_SUCCESS.value,
            "filename": new_filename
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id:str , process_request: ProcessRequest):
    file_id = process_request.file_id   
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    
    file_chunks = process_controller.process_file_content(file_content=file_content, file_id=file_id, chunk_size=chunk_size, overlap_size=overlap_size)

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Signal": ResponseSignals.FILE_PROCESSING_FAILED.value}
        )
    return file_chunks
