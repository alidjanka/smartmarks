from typing import List
from pydantic import BaseModel

from config import Config
from authenticate import SupabaseAuthenticator

from pydantic_ai import Agent
from custom_agents import url_reduction_agent, url_summary_agent
from supabase import Client

class URLData(BaseModel):
    url: str
    reduced_url: str
    summary: str
    user_id: str

class Bookmark(BaseModel):
    title: str
    url: str
    md_content: str

class BookmarkProcessor():
    def __init__(self, authenticated_supabase_client: Client, url_reduction_agent: Agent, url_summary_agent: Agent, table="bookmarks"):
        self.client = authenticated_supabase_client
        self.user_id = self.client.auth.get_user().user.id
        self.url_reduction_agent = url_reduction_agent
        self.url_summary_agent = url_summary_agent
        self.table = table

    def url_exists(self, url: str) -> bool:
        response = self.client.table(self.table).select("id").eq("url", url).execute()
        return len(response.data) > 0

    def reduce_url(self, url: str) -> dict:
        # run sync takes time, try async
        reduction_request = self.url_reduction_agent.run_sync('', deps=url)
        return reduction_request.data
    
    def generate_description(self, bookmark: Bookmark) -> dict:
        summary_request = self.url_summary_agent.run_sync('', deps=bookmark)
        return summary_request.data

    def insert_data(self, url_data: URLData):
        response = self.client.table(self.table).insert(url_data.model_dump()).execute()
        return response

    def save_bookmarks(self, bookmarks: List[Bookmark], table_name: str):
        for bookmark in bookmarks:
            try:
                if self.url_exists(bookmark.url):
                    print(f"URL already exists in the database: {bookmark.url}")
                    continue

                # llm_response = self.reduce_url(url)
                llm_response = self.generate_description(bookmark)
                url_data = URLData(
                    url=bookmark.url,
                    title=bookmark.title,
                    llm_description=llm_response.llm_description,
                    user_id=self.user_id
                )

#                url_data = URLData(
#                    url=url,
#                    reduced_url=llm_response.reduced_url,
#                    summary=llm_response.summary,
#                    user_id=self.user_id
#               )
                response = self.insert_data(url_data)
                print(f"Inserted data for URL: {bookmark.url} | Response: {response}")
            except Exception as e:
                print(f"Error processing URL: {bookmark.url} | Error: {str(e)}")


# Example usage
if __name__ == "__main__":
    auth = SupabaseAuthenticator()
    #sign_up_response = auth.sign_up("alicann91@gmail.com", "hedehodo")
    #print(sign_up_response)
    sign_in_response = auth.sign_in_with_password("alicann91@gmail.com", "hedehodo")
    user_id = auth.get_user_id()
    authenticated_client = auth.get_client()

    if user_id is not None:
        processor = BookmarkProcessor(authenticated_client, url_reduction_agent)
        input_urls = ["https://medium.com/analytics-vidhya/a-gentle-introduction-to-data-workflows-with-apache-airflow-and-apache-spark-6c2cd9aee573"]
        table_name = "bookmarks"

        #processor.save_bookmarks(input_urls, table_name)

        test_data = URLData(url="www.example.com", reduced_url="example.com", summary="test", user_id=user_id)
        processor.insert_data(url_data=test_data)
    else:
        print("User id is NONE!!!")
