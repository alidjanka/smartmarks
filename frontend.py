import json
import asyncio 
import streamlit as st
from data_extractor import DataExtractor, Bookmark
from bookmark_processor import BookmarkProcessor
from retrieve import BookmarksVectorSchema, PineconeRetriever
from custom_agents import LabelerDeps
import aiofiles

with open('/home/alican/Desktop/Projects/smartmarks/processed_bookmarks.json') as file:
    unprocessed_bookmarks = json.load(file)    
bookmarks = [] # None

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

async def generate_labels(bookmarks):
    bookmark_processor = BookmarkProcessor()
    label_generator_response = await bookmark_processor.generate_labels(bookmarks)
    return label_generator_response.labels

async def get_labeled_bookmarks(bookmarks, labels):
    bookmark_processor = BookmarkProcessor()
    labeled_bookmarks = []
    for bookmark in bookmarks:
        try:
            deps = LabelerDeps(bookmark=bookmark, labels=labels)
            agent_response = await bookmark_processor.labeler_agent(deps)
            predicted_labels = agent_response.labels
            labeled_bookmarks.append((predicted_labels, bookmark))
        except Exception as e:
            print(f"Error processing bookmark {bookmark.url}: {e}")
    return labeled_bookmarks

DEFAULT_LABELS = "Work,Read Later,Miscellaneous,"
uploaded_file = st.file_uploader("Choose a file")

# extract urls
if uploaded_file is not None:
    #bookmark_extractor = DataExtractor(uploaded_file)
    #bookmarks = bookmark_extractor.extract_bookmarks() 
    for b in unprocessed_bookmarks:
        bookmarks.append(Bookmark(title=b['title'], url=b['url'], md_content=b['description']))
    generated_labels = asyncio.run(generate_labels(bookmarks))
    label_string = DEFAULT_LABELS + generated_labels
    st.write(label_string)
    labels = label_string.split(',')  
    labeled_bookmarks = asyncio.run(get_labeled_bookmarks(bookmarks, label_string))
else:
    labeled_bookmarks = None
if st.button("AutoLabel", type="primary") and labeled_bookmarks is not None:
# generate labels for all bookmarks
    options = st.multiselect("Labels", labels)
    matching_bookmarks = [bookmark for label, bookmark in labeled_bookmarks if label in options]
    for labeled_bookmark in matching_bookmarks:
        st.write(labeled_bookmark.url)        

# generate description for url  
    #processed_bookmarks = asyncio.run(process_bookmarks(bookmarks))
# embed and upsert
    #namespace = str(processed_bookmarks[0]["user_id"])
    #embedder_obj = PineconeRetriever(index_name='smartmarks', namespace=namespace)
    #embedder_obj.upsert(processed_bookmarks)
# query