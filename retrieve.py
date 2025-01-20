import json
import time
from pydantic import BaseModel
from typing import List

from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec

from config import Config

class BookmarksVectorSchema(BaseModel):
    user_id: str
    id: str
    url: str 
    title: str
    description: str

class PineconeRetriever:
    def __init__(self, index_name: str, namespace: str):
        self.pc = Pinecone(api_key=Config.PINECONE_KEY)
        if not self.pc.has_index(index_name):
            self.pc.create_index(
                name=index_name,
                dimension=1024,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud='aws', 
                    region='us-east-1'
                ) 
            ) 
            while not self.pc.describe_index(index_name).status['ready']:
                time.sleep(1)
        self.index = self.pc.Index(index_name)
        self.namespace = namespace
    def split_into_chunks(self, data: List[BookmarksVectorSchema], chunk_size=96):
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    def upsert(self, data: List[BookmarksVectorSchema]):
        chunks = self.split_into_chunks(data)
        for data in chunks:
            embeddings = self.pc.inference.embed(
                model="multilingual-e5-large",
                inputs=[f"{d['title']}\n{d['description']}" for d in data],
                parameters={"input_type": "passage", "truncate": "END"}
            )
            records = []
            for d, e in zip(data, embeddings):
                records.append({
                    "id": d['id'],
                    "values": e['values'],
                    # change metadata
                    "metadata": {'url': d['url'], 'title': d['title']}
                })
            # Upsert the records into the index
            self.index.upsert(
                vectors=records,
                namespace=self.namespace
            )       
    def query(self, q, top_k=5):
        query_embedding = self.pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[q],
            parameters={
                "input_type": "query"
            }
        )
        results = self.index.query(
            namespace=self.namespace,
            vector=query_embedding[0].values,
            top_k=top_k,
            include_values=False,
            include_metadata=True
        )
        return results
    def retrieve_embeddings(self, batch_size=10):
        vector_data = self.index.fetch(ids=[str(x) for x in range(1,batch_size+1)], namespace=self.namespace)
        vectors = vector_data["vectors"]
        return vectors
#    def get_recommendations(self, results):
#        return results['matches']

if __name__ == "__main__":
    #with open("processed_bookmarks.json", 'r') as file:
    #    data = json.load(file)
    embedder_obj = PineconeRetriever(index_name='smartmarks', namespace='0')
    vectors = embedder_obj.retrieve_embeddings()
    print(vectors)

    