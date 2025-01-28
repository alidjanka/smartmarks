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
elif st.button("Cluster"):
    clustered_data = pinecone_obj.fetch_and_cluster(batch_size=300, min_cluster_size=3)
    try:
        with open('clustered_data.json', 'w') as file:
            json.dump(clustered_data, file, indent=4)
    except:
        pass
    with st.expander("0"):
        for item in clustered_data:
            if item['cluster'] == "0":
                st.write(item["url"])
    with st.expander("1"):
        for item in clustered_data:
            if item['cluster'] == "1":
                st.write(item["url"])
    with st.expander("2"):
        for item in clustered_data:
            if item['cluster'] == "2":
                st.write(item["url"])
        print("finished")
