from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from config import Config
import json
from pydantic import BaseModel

class PineconeData(BaseModel):
    id: int
    url: str 
    title: str
    description: str

class PineconeRetriever:
    def __init__(self, index_name, namespace):
        self.pc = Pinecone(api_key=Config.PINECONE_KEY)
        self.index = self.pc.Index(index_name)
        self.namespace = namespace
    def split_into_chunks(self, data, chunk_size=96):
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    def upsert(self, data):
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
                    "metadata": {'url': d['url']}
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
    def retrieve_embeddings(self, batch_size=100):
        vectors = {}
        query = {"namespace": self.namespace} if self.namespace else {}
        for vec in self.index.fetch_all_metadata(**query, batch_size=batch_size):
            vectors.update(vec)
        return vectors
#    def get_recommendations(self, results):
#        return results['matches']

if __name__ == "__main__":
    with open("movies_latest_2.json", 'r') as file:
        data = json.load(file)
    embedder_obj = PineconeRetriever(index_name='my_index', namespace='my_namespace')
    embedder_obj.upsert(data)

    