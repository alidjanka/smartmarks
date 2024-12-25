from datetime import datetime
from typing import List
from pydantic import BaseModel
from uuid import UUID

from config import Config
from authenticate import SupabaseAuthenticator

from pydantic_ai import Agent
from custom_agents import url_reduction_agent

from supabase import create_client, Client

# Pydantic models
class URLData(BaseModel):
    url: str
    reduced_url: str
    summary: str
    user_id: str

class BookmarkProcessor():
    def __init__(self, authenticated_client: Client, url_reduction_agent: Agent):
        self.client = authenticated_client
        self.user_id = self.client.auth.get_user().user.id
        self.url_reduction_agent = url_reduction_agent

    def url_exists(self, table_name: str, url: str) -> bool:
        response = self.client.table(table_name).select("id").eq("url", url).execute()
        return len(response.data) > 0

    def reduce_url(self, url: str) -> dict:
        # run sync takes time, try async
        reduction_request = self.url_reduction_agent.run_sync('', deps=url)
        return reduction_request.data

    def insert_data(self, table_name: str, url_data: URLData):
        response = self.client.table(table_name).insert(url_data.model_dump()).execute()
        return response

    def save_bookmarks(self, input_urls: List[str], table_name: str):
        for url in input_urls:
            try:
                if self.url_exists(table_name, url):
                    print(f"URL already exists in the database: {url}")
                    continue

                llm_response = self.reduce_url(url)
                url_data = URLData(
                    url=url,
                    reduced_url=llm_response.reduced_url,
                    summary=llm_response.summary,
                    user_id=self.user_id
                )
                # table name seems to be public.urls which cant be accessed
                response = self.insert_data(table_name, url_data)
                print(f"Inserted data for URL: {url} | Response: {response}")
            except Exception as e:
                print(f"Error processing URL: {url} | Error: {str(e)}")

# Example usage
if __name__ == "__main__":
    auth = SupabaseAuthenticator("alicann91@gmail.com", "hedehodo")
    #sign_up_response = auth.sign_up()
    #print(sign_up_response)
    sign_in_response = auth.sign_in_with_password()
    user_id = auth.get_user_id()
    authenticated_client = auth.get_client()

    if user_id is not None:
        processor = BookmarkProcessor(authenticated_client, url_reduction_agent)
        input_urls = ["https://medium.com/analytics-vidhya/a-gentle-introduction-to-data-workflows-with-apache-airflow-and-apache-spark-6c2cd9aee573"]
        table_name = "bookmarks"

        #processor.save_bookmarks(input_urls, table_name)

        test_data = URLData(url="www.example.com", reduced_url="example.com", summary="test", user_id=user_id)
        processor.insert_data(table_name=table_name, url_data=test_data)
    else:
        print("User id is NONE!!!")
