import json
import asyncio 
import streamlit as st
from data_extractor import DataExtractor
from bookmark_processor import BookmarkProcessor, BookmarksSchema
from retrieve import PineconeRetriever

query = st.text_input("Search bookmarks")

# extract urls
#with open('processed_bookmarks.json') as file:
#    processed_bookmarks = json.load(file)    

pinecone_obj = PineconeRetriever(index_name='smartmarks', namespace="0")
# query
if st.button("Search"):
    if len(query) > 0:
        results = pinecone_obj.query(query)
        for match in results["matches"]:
            st.write(match["metadata"]["url"])
    else:
        st.write("Query is empty")