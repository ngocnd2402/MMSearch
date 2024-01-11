# MEILISEARCH FUNCTIONS UTILITIES
import meilisearch
import json

class Meilisearch:

    def __init__(self, index_name, port = 5555):
        self.index_name = index_name   
        self.client = meilisearch.Client(f'http://localhost:{port}')
    
    def check_health_status(self) -> bool:
        return self.client.is_healthy()
    
    def create(self, primary_key:str = "id"):
        self.client.create_index(uid=self.index_name, options={'primaryKey': primary_key})

    def insert(self, json_file_path:str):
        with open(json_file_path) as json_file:
            data = json.load(json_file)
        self.client.index(self.index_name).update_documents(data)

    def delete(self):
        self.client.delete_index(self.index_name)

    def query(self, query_text:str, k:int = 80) -> list:
        return self.client.index(self.index_name).search(
            query_text, 
            {"limit" : k}
        )["hits"]


