from pydantic import BaseModel
from typing import Optional


class ProcessRequest(BaseModel):
    project_id: str
    file_id: str
    chunk_size: Optional[int] =  100  # Default chunk size 
    overlap_size: Optional[int] = 20  # Default overlap size
    do_reset: Optional[int] = 0  # Default to not reset
    



