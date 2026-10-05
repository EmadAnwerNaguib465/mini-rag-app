from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignals
from .ProjectController import ProjectController
import re 
import os

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_limit_mb = self.app_settings.FILE_MAX_SIZE_MB

    def validate_file(self,file:UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False,ResponseSignals.FILE_TYPE_NOT_SUPPORTED.value
        if file.size > self.app_settings.FILE_MAX_SIZE_MB * 1024 * 1024:
            return False ,ResponseSignals.FILE_SIZE_EXCEEDED.value
        return True ,ResponseSignals.FILE_VALIDATED_SUCCESS.value

    def generate_unique_filepath(self, original_filename: str, project_id: str):
        random_file_name = self.generate_random_string()

        project_path = ProjectController().get_project_file(
            project_id=project_id
        )

        clean_filename = self.get_clean_file_name(
            original_filename=original_filename
        )

        new_filename = f"{random_file_name}_{clean_filename}"

        unique_filename = os.path.join(
            project_path,
            new_filename
        )

        while os.path.exists(unique_filename):
            random_file_name = self.generate_random_string()
            new_filename = f"{random_file_name}_{clean_filename}"

            unique_filename = os.path.join(
                project_path,
                new_filename
            )

        return (
            new_filename,
            random_file_name,
            "_",
            clean_filename
        )
            

    def get_clean_file_name (self, original_filename: str):
        # Remove any Special characters ,except underscores and .
        clean_filename = re.sub(r'[^\w\_\.]', '', original_filename)
        clean_filename = clean_filename.replace(" ", "_")  # Replace spaces with underscores
        
        return clean_filename
        
        