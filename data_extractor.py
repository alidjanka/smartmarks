from bs4 import BeautifulSoup
import requests
from markdownify import markdownify as md
from io import StringIO
from pydantic import BaseModel

class Bookmark(BaseModel):
    title: str
    url: str
    md_content: str

class DataExtractor:
    def __init__(self, uploaded_file=None, file_path=None):
            if uploaded_file is not None:
            # To convert to a string based IO:
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                self.content = stringio.read()
            elif file_path is not None:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.content = file.read()
            else:
                self.content = None       
    def extract_bookmarks(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        bookmarks = []

        for a_tag in soup.find_all('a', href=True):
            url = a_tag['href']
            try:
                response = requests.get(url)
                # Check if the request was successful
                if response.status_code == 200:
                    html_content = response.text
                    md_content = md(html_content)
                else:
                    print(f"Failed to retrieve the page. Status code: {response.status_code}")
                    md_content = ''
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                continue
            title = a_tag.get_text()
            bookmark = Bookmark(title=title, url=url, md_content=md_content)
            bookmarks.append(bookmark)
        
        return bookmarks
    
if __name__ == "__main__":
    extractor = DataExtractor()
    bookmarks=extractor.extract_bookmarks('/home/alican/Documents/bookmarks_1_17_25.html')
    print(len(bookmarks))
    print(bookmarks[1])
