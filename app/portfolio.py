import pandas as pd
import chromadb
import uuid
        

class Portfolio:
    def __init__(self, file_path="resource/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(documents=row["Techstack"],
                                    metadatas={"links": row["Links"]},
                                    ids=[str(uuid.uuid4())])

    def query_links(self, role):
        if not role:
            return []

        if isinstance(role, str):
            role = [role]

        query_result = self.collection.query(query_texts=role, n_results=2)

        # Ensure it's a dict and 'metadatas' exists
        if isinstance(query_result, dict) and 'metadatas' in query_result:
            return query_result['metadatas']
        else:
            return []

