from fastapi import FastAPI, APIRouter, Depends, UploadFile ,status ,Request
from fastapi.responses import JSONResponse
import os
from helper.config import get_settings, Settings
from controllers import DataController , ProjectController , ProcessController
import aiofiles
from models import ResponseSignals
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from models.enums.AssetTypeEnum import AssetTypeEnum


logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
    )

@data_router.post("/upload/{project_id}")
async def upload_file(
    request :Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)

):
    project_model =await ProjectModel.create_instance(
        db_client = request.app.db_client
    )


    project = await project_model.get_project_or_create_one(project_id =project_id)

     
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

    # store the assets into the database

    asset_model = await AssetModel.create_instance(
        db_client = request.app.db_client
    )

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=new_filename,
        asset_size=os.path.getsize(file_path),
    )

    asset_record = await asset_model.create_asset(asset =asset_resource )

    return JSONResponse(
        content={
            "Signal": ResponseSignals.FILE_UPLOAD_SUCCESS.value,
            "filename": str(asset_record.id),
        }
    )

    
@data_router.post("/process/{project_id}")
async def process_endpoint(
    request: Request,
    project_id: str,
    process_request: ProcessRequest = ProcessRequest(),
):
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client = request.app.db_client
       )
    
    project = await project_model.get_project_or_create_one(project_id =project_id)

    asset_model = await AssetModel.create_instance(
            db_client = request.app.db_client) 
    
    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
             asset_project_id=project.id,
             asset_name=process_request.file_id
        )
        if asset_record is None:
             return JSONResponse(
                     status_code=status.HTTP_400_BAD_REQUEST,
                     content={
                         "Signal": ResponseSignals.FILE_ID_ERROR.value,
                     })
             
        project_files_ids = {
             asset_record.id :asset_record.asset_name
        }
    else :
        

        project_file = await asset_model.get_all_projects_assets(asset_project_id =project.id, asset_type = AssetTypeEnum.FILE.value)
        project_files_ids = {
                    record.id : record.asset_name
                    for record in project_file
        }

        

    if len(project_files_ids) == 0:
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "Signal": ResponseSignals.NO_FILES_ERROR.value,
        })


    process_controller = ProcessController(project_id=project_id)

    no_records = 0
    no_files = 0

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    
    if do_reset == 1:
                deleted_count = await chunk_model.delete_chunk_by_project_id(project_id=project.id)
                logger.info(f"Deleted {deleted_count} chunks for project {project_id} due to reset request.")   
    

    for asset_id,file_id in project_files_ids.items():

        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
             logger.error(f"Error while processing file {file_id}")
             continue
        
        file_chunks = process_controller.process_file_content(file_content=file_content, file_id=file_id, chunk_size=chunk_size, overlap_size=overlap_size)

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"Signal": ResponseSignals.FILE_PROCESSING_FAILED.value}
            )
        
        file_chunk_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.id, 
                chunk_asset_id=asset_id
            )   
            for i ,chunk in enumerate(file_chunks)
        ]

    
        no_records += await chunk_model.insert_many_chunk(chunks = file_chunk_records)
        no_files += 1


    return JSONResponse(
        content={
            "Signal": ResponseSignals.FILE_PROCESSING_SUCCESS.value,
            "total_chunks": no_records,
            "processed_files" : no_files
        })
    
