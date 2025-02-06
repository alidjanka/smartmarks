from typing import List
from pydantic import BaseModel

from authenticate import SupabaseAuthenticator
from data_extractor import Bookmark

from custom_agents import url_reduction_agent, url_summary_agent, label_generator_agent, labeler_agent, LabelerDeps
from supabase import Client

class URLData(BaseModel):
    url: str
    reduced_url: str
    summary: str
    user_id: str

class BookmarksSchema(BaseModel):
    user_id: int
    url: str 
    title: str
    description: str

class BookmarkProcessor():
    def __init__(self, authenticated_supabase_client: Client=None, table_name: str="bookmarks"):
        self.client = authenticated_supabase_client
        if self.client is not None:
            self.user_id = self.client.auth.get_user().user.id
        else:
            self.user_id = None
        self.url_reduction_agent = url_reduction_agent
        self.url_summary_agent = url_summary_agent
        self.label_generator_agent = label_generator_agent
        self.labeler_agent = labeler_agent
        self.table = table_name

    def url_exists(self, url: str) -> bool:
        response = self.client.table(self.table).select("id").eq("url", url).execute()
        return len(response.data) > 0

    def reduce_url(self, url: str) -> dict:
        # run sync takes time, try async
        reduction_request = self.url_reduction_agent.run_sync('', deps=url)
        return reduction_request.data
    
    async def generate_description(self, bookmark: Bookmark) -> dict:
        summary_request = await self.url_summary_agent.run('', deps=bookmark)
        return summary_request.data
    
    async def generate_labels(self, bookmarks: List[Bookmark]) -> dict:
        label_request = await self.label_generator_agent.run('', deps=bookmarks)
        return label_request.data
    
    async def label_bookmarks(self, labeler_deps: LabelerDeps) -> dict:
        labeler_request = await self.labeler_agent.run('', deps=labeler_deps)
        return labeler_request.data

    def insert_data(self, url_data: URLData):
        response = self.client.table(self.table).insert(url_data.model_dump()).execute()
        return response

    def save_bookmarks(self, bookmarks: List[Bookmark]):
        for bookmark in bookmarks:
            try:
                if self.url_exists(bookmark.url):
                    print(f"URL already exists in the database: {bookmark.url}")
                    continue

                # llm_response = self.reduce_url(url)
                llm_response = self.generate_description(bookmark)
                url_data = BookmarksSchema(
                    url=bookmark.url,
                    title=bookmark.title,
                    description=llm_response.llm_description,
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
