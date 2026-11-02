from qdrant_client import QdrantClient , models
from ..VectorDBInteface import VectorDBInterface 
from ..VectorDBEnums import VectorDBEnums ,DistanceMethodEnums
import logging
from typing import List

class QdrantDBProvider(VectorDBInterface):

    def __init__(self,db_path:str , distance_method:str):

        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        elif distance_method == DistanceMethodEnums.EUCLIDEAN.value:    
            self.distance_method = models.Distance.EUCLIDEAN

        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        self.logger.info(f"Connected to QdrantDB at {self.db_path}")

    def disconnect(self):
        self.client =None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    def create_collection(self, collection_name: str,
                               embedding_size: int, 
                               do_reset: bool = False):
        if do_reset:
            _=self.delete_collection(collection_name=collection_name)


        if not self.is_collection_existed(collection_name=collection_name):
            _= self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            return True
        return False

    def insert_one(self, collection_name: str,
                    text: str, vector: List, 
                    metadata: dict,
                    record_id: str = None):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False
        try:
            _= self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        vector=vector,
                        payload={"text": text, "metadata": metadata} 
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error inserting record: {e}")
            return False
        return True
    
    def insert_many(self, collection_name: str,
                         texts: List[str], vectors: List[List],
                         metadatas: List[dict] = None,
                         record_ids: List[str] = None,
                         batch_size: int = 50):
        if metadatas is None:
            metadatas = [None] * len(texts)

        if record_ids is None:
            record_ids = [None] * len(texts)

        for i in range(0, len(texts),batch_size):
            batch_end = i + batch_size

            batch_texts= texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadatas[i:batch_end]

            batch_records = [
                models.Record(
                    vector=batch_vectors[x],
                    payload={"text": batch_texts[x] , "metadata": batch_metadata[x]}
                )
                for x in range(len(batch_texts))
            ]
            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                    )
            except Exception as e:
                self.logger.error(f"Error inserting batch starting at index {i}: {e}")
                return False
            return True

    def search_by_vector(self, collection_name: str,
                         vector: List,
                         limit:int=5) :
        return self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

        


