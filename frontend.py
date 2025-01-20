import json
import asyncio 
import streamlit as st
from data_extractor import DataExtractor
from bookmark_processor import BookmarkProcessor
from retrieve import BookmarksVectorSchema, PineconeRetriever
import aiofiles

uploaded_file = st.file_uploader("Choose a file")

async def process_bookmarks(bookmarks):
    bookmark_processor = BookmarkProcessor()
    processed_bookmarks = []
    for i, bookmark in enumerate(bookmarks):
        try:
            agent_response = await bookmark_processor.generate_description(bookmark)
            processed_bookmark = BookmarksVectorSchema(user_id=str(0), id=str(i+1), url=bookmark.url, title=bookmark.title, description=agent_response.llm_description)      
            processed_bookmarks.append(processed_bookmark)
        except Exception as e:
            print(f"Error processing bookmark {bookmark.url}: {e}")
    #async with aiofiles.open("processed_bookmarks.json", "w") as file:
    #    await file.write(json.dumps([bookmark.dict() for bookmark in processed_bookmarks], indent=4))
    return processed_bookmarks

# extract urls
if uploaded_file is not None:
    bookmark_extractor = DataExtractor(uploaded_file)
    bookmarks = bookmark_extractor.extract_bookmarks() 
# generate description for url  
    processed_bookmarks = asyncio.run(process_bookmarks(bookmarks))
# embed and upsert
    namespace = str(processed_bookmarks[0]["user_id"])
    embedder_obj = PineconeRetriever(index_name='smartmarks', namespace=namespace)
    embedder_obj.upsert(processed_bookmarks)
# query