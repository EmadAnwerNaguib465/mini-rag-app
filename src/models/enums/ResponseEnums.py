from enum import Enum

class ResponseSignals(Enum):


    FILE_VALIDATED_SUCCESS = "File validated successfully."
    FILE_TYPE_NOT_SUPPORTED = "File type not supported."  
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum limit."
    FILE_UPLOAD_FAILED = "File upload failed."
    FILE_UPLOAD_SUCCESS = "File uploaded successfully."
    FILE_PROCESSING_FAILED = "File processing failed."
    FILE_PROCESSING_SUCCESS = "File processed successfully."
    NO_FILES_ERROR = "Not found files"
    FILE_ID_ERROR = "no file found with this id"

