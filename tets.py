from data_extractor import Bookmark
from bookmark_processor import BookmarkProcessor, BookmarksSchema


bk = Bookmark(title='LangGraph Glossary', url='https://langchain-ai.github.io/langgraph/concepts/low_level/#graphs', md_content='Internal Server Error')
bk_pr = BookmarkProcessor()
desc = bk_pr.generate_description(bk)
print(desc.llm_description)