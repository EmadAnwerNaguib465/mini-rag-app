from enum import Enum

class ResponseSignals(Enum):


    FILE_VALIDATED_SUCCESS = "File validated successfully."
    FILE_TYPE_NOT_SUPPORTED = "File type not supported."  
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum limit."
    FILE_UPLOAD_FAILED = "File upload failed."
    FILE_UPLOAD_SUCCESS = "File uploaded successfully."
