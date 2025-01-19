import json
import asyncio 
import streamlit as st
from data_extractor import DataExtractor
from bookmark_processor import BookmarkProcessor, BookmarksSchema
import aiofiles

uploaded_file = st.file_uploader("Choose a file")

async def process_bookmarks(bookmarks):
    bookmark_processor = BookmarkProcessor()
    processed_bookmarks = []
    for bookmark in bookmarks:
        try:
            agent_response = await bookmark_processor.generate_description(bookmark)
            processed_bookmark = BookmarksSchema(user_id=0, url=bookmark.url, title=bookmark.title, description=agent_response.llm_description)      
            processed_bookmarks.append(processed_bookmark)
        except Exception as e:
            print(f"Error processing bookmark {bookmark.url}: {e}")
    async with aiofiles.open("processed_bookmarks.json", "w") as file:
        await file.write(json.dumps([bookmark.dict() for bookmark in processed_bookmarks], indent=4))

# extract urls
if uploaded_file is not None:
    bookmark_extractor = DataExtractor(uploaded_file)
    bookmarks = bookmark_extractor.extract_bookmarks() 
# generate description for url
    
    asyncio.run(process_bookmarks(bookmarks))

    
# embed and upsert
# query