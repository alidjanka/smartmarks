import json
import asyncio 
import streamlit as st
import time
from data_extractor import DataExtractor, Bookmark
from bookmark_processor import BookmarkProcessor
from custom_agents import LabelerDeps
import aiofiles
from collections import defaultdict
from typing import List

from clustering import cluster_agent, cluster_assigner

if "clusters" not in st.session_state:
    st.session_state.clusters = []
if "clustered_urls" not in st.session_state:
    st.session_state.clustered_urls = None

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    bookmark_extractor = DataExtractor(uploaded_file)
    bookmarks = bookmark_extractor.extract_bookmarks(with_content=False) 
else:
    with open('/home/alican/Desktop/Projects/smartmarks/processed_bookmarks.json') as file:
        unprocessed_bookmarks = json.load(file)    
    bookmarks = [] 
    for b in unprocessed_bookmarks:
        bookmark = Bookmark(title=b['title'], url=b['url'], md_content=b['id'])
        bookmarks.append(bookmark)

st.write(f"Amount of bookmarks: {len(bookmarks)}")

async def cluster(bookmarks: List[Bookmark]):
    response = await cluster_agent.run("Generate cluster names", deps=bookmarks)
    return response.data.cluster_names

async def assign_cluster(bookmarks: List[Bookmark], clusters):
    clustered_bookmarks = defaultdict(list)
    for bookmark in bookmarks:
        response = await cluster_assigner.run("Assign the URL to one of these clusters: " + str(clusters), deps=bookmark)
        clustered_bookmarks[response.data.cluster_name].append(bookmark.url)
    return clustered_bookmarks

# Button to trigger clustering
if st.button("Cluster"):
    start_time = time.time()
    st.session_state.clusters = asyncio.run(cluster(bookmarks))
    st.session_state.clustered_urls = asyncio.run(assign_cluster(bookmarks, st.session_state.clusters))

    end_time = time.time()
    st.write(f"Elapsed time: {end_time - start_time}")
    total_urls = sum(len(clustered_url) for clustered_url in st.session_state.clustered_urls.values())
    st.write(f"Total clustered urls: {total_urls}")

# Dropdown selection
if st.session_state.clusters:
    option = st.selectbox("Filter:", st.session_state.clusters)
    if st.session_state.clustered_urls and option is not None:
        for url in st.session_state.clustered_urls[option]:
            st.write(url)

