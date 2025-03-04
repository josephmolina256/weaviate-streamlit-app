from typing import List, Dict, Optional
import traceback
import weaviate
import weaviate.connect as wvc
from weaviate.classes.query import Filter
from sentence_transformers import SentenceTransformer

from constants import HF_EMBEDDING_MODEL_NAME

class WeaviateInterface:
    def __init__(self, generate_embeddings: bool = True, hf_model_name: str = "multi-qa-distilbert-cos-v1"):
        self.generate_embeddings = generate_embeddings
        if generate_embeddings:
            self.embedding_model = SentenceTransformer(hf_model_name)
        self.client = weaviate.connect_to_local()
        assert self.client.is_live()

    def check_connection(self) -> bool:
        return self.client.is_live()

    def client_reconnect(self) -> bool:
        try:
            self.client = weaviate.connect_to_local()
            assert self.client.is_live()
        except Exception as e:
            print("An error occurred in Storer.client_reconnect:")
            traceback.print_exc()
            return False
        print("Reconnected to Weaviate client.")
        return True

    def client_close(self) -> bool:
        try:
            self.client.close()
        except Exception as e:
            print("An error occurred in Storer.client_close:")
            traceback.print_exc()
            return False
        print("Closed Weaviate client.")
        return True

    def store(self, 
              input_data: List[Dict],  
              collections_name: str, 
              text_to_be_embedded: Optional[str] = None, 
              embeddings: Optional[List[List[float]]] = None
        ) -> Dict[str, str]:
        if self.generate_embeddings:
            assert text_to_be_embedded
        else:
            assert embeddings
            assert len(input_data) == len(embeddings)

        assert self.client.is_live()

        try:            
            wv_objs = list()

            for i in range(len(input_data)):
                properties = input_data[i]

                if self.generate_embeddings:
                    embedding = self.embedding_model.encode(text_to_be_embedded).tolist()
                else:
                    embedding = embeddings[i]

                wv_objs.append(wvc.data.DataObject(
                    properties=properties,
                    vector=embedding
                ))

            collection = self.client.collections.get(collections_name)
            if collection is None:
                collection = self.client.collections.create(
                    collections_name,
                    vectorizer_config=wvc.config.Configure.Vectorizer.none(),
                )

            collection.data.insert_many(wv_objs)
            print("Stored successfully!")
            return {"status": f"Stored {len(wv_objs)} items successfully!"}
        except Exception as e:
            print("An error occurred in Storer.store:")
            traceback.print_exc()
            self.client.close()
            return {"status": f"an error occurred {e}"}

    def retrieve(self, 
                  query: str, 
                  collections_name: str, 
                  query_embedding: Optional[List[float]] = None, 
                  limit: int = 3, 
                  certainty_threshold: float = 0.5
        ) -> Optional[List[Dict]]:
        assert self.generate_embeddings or query_embedding
        assert self.client.is_live()
        
        try:
            collection = self.client.collections.get(collections_name)
            if self.generate_embeddings:
                query_embedding = self.embedding_model.encode(query).tolist()
            else:
                assert type(query_embedding) == list

            response = collection.query.near_vector(
                near_vector=query_embedding,
                limit=limit,
                return_metadata=wvc.query.MetadataQuery(certainty=True),
                certainty=certainty_threshold,
            )

            res = []
            for obj in response.objects:
                res.append(
                    {
                        "certainty": obj.metadata.certainty,
                        "properties": obj.properties
                    }
                )

            if len(res) == 0:
                print("No results found.")
                return None
            return res
        except Exception as e:
            print("An error occurred in Storer.retrieve:")
            traceback.print_exc()
            self.client.close()

    def update_item(
            self, 
            collections_name: str, 
            item: Dict,
            updated_text: str, 
            key_to_be_updated: str
        ) -> Dict:

        updated_item = item
        updated_item[key_to_be_updated] = updated_text

        text_to_be_embedded = updated_item["head"]

        if key_to_be_updated == "responses":
            text_to_be_embedded += updated_item["responses"]

        store_result = self.store(
            collections_name=collections_name,
            input_data=[item],
            text_to_be_embedded=text_to_be_embedded
        )
        if store_result["status"].startswith("Stored"):
            self.delete_item(
                collections_name, 
                item["uuid"], 
                item["thread_ts"]
            )
        else:
            updated_item = {"status": "update failed"}
        return updated_item

        

        

    def delete_item(
            self, 
            collections_name: str,
            uuid: Optional[str],
            thread_ts: Optional[str]
        ) -> Dict:
        collection = self.client.collections.get(collections_name)

        if uuid:
            result = collection.data.delete_by_id(uuid)
            deleted_item = {"uuid": uuid, "status": "deleted"}
        elif thread_ts:
            result = collection.data.delete_many(
                where=Filter.by_property("thread_ts").like(thread_ts),
                verbose=True
            )
            deleted_item = {"thread_ts": thread_ts, "status": "deleted"}
        else:
            result = {"status": "No UUID or thread_ts provided."}

        print(result)
        return deleted_item
    
    # def delete_all_items(self, collections_name: str) -> Dict:
    #     collection = self.client.collections.get(collections_name)
    #     result = collection.data.delete_many(
    #         where=Filter.by_property("thread_ts").like("*"),
    #         dry_run=True,
    #         verbose=True
    #     )
    #     return result

    
    def get_collection_names(self) -> list[str]:
        assert self.client.is_live()

        try:
            collections = list(self.client.collections.list_all().keys())
            return collections
        except Exception as e:
            print("An error occurred in Storer.view_collections:")
            traceback.print_exc()

    def view_contents_of_collection(self, collection_name: str) -> List[Dict]:
        assert self.client.is_live()

        try:
            collection = self.client.collections.get(collection_name)
            contents = collection.iterator()
            content_properties = [content.properties for content in contents]

            if len(content_properties) == 0:
                print("No contents found.")
                return None
            return content_properties
        except Exception as e:
            print("An error occurred in Storer.view_contents_of_collection:")
            traceback.print_exc()