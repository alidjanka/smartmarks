import json
import asyncio
import streamlit as st
import time
import pandas as pd
from data_extractor import DataExtractor, Bookmark
from bookmark_processor import BookmarkProcessor
from typing import List

CACHE_FILE = "cached_bookmarks.json"  # File to store cached bookmarks

bookmark_processor = BookmarkProcessor()

# Load cached bookmarks from file/ this needs to go to DB
@st.cache_data
def load_cached_bookmarks():
    try:
        with open(CACHE_FILE, "r") as file:
            cached_data = json.load(file)
        return [Bookmark(**b) for b in cached_data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save bookmarks to cache
def save_bookmarks_to_cache(bookmarks):
    with open(CACHE_FILE, "w") as file:
        json.dump([b.model_dump() for b in bookmarks], file)

# Initialize session state for clusters and filtered bookmarks
if "clusters" not in st.session_state:
    st.session_state.clusters = []
if "clustered_urls" not in st.session_state:
    st.session_state.clustered_urls = None
if "filtered_bookmarks" not in st.session_state:
    st.session_state.filtered_bookmarks = []

# Load cached bookmarks if available
cached_bookmarks = load_cached_bookmarks()

# Function to show bookmarks as cards
def show_cards(bookmarks):
    if not bookmarks:
        st.warning("No bookmarks to display.")
        return

    bookmarks_df = pd.DataFrame([b.model_dump(exclude={'md_content'}) for b in bookmarks]).sort_values('added_date', ascending=False)
    N_cards_per_row = 3
    cols = st.columns(N_cards_per_row, gap="large")

    for n_row, row in bookmarks_df.iterrows():
        with cols[n_row % N_cards_per_row]:
            st.caption(f"📌 {row['title']}")
            st.markdown(f"**Cluster:** {row['cluster'] or 'Unassigned'}")
            st.markdown(f"📅 *Added on:* {row['added_date'] or 'Unknown'}")
            st.markdown(f"🔗 [Visit]({row['url']})")

# File uploader
uploaded_file = st.file_uploader("📂 Upload a File")

if uploaded_file:
    bookmark_extractor = DataExtractor(uploaded_file)
    bookmarks = bookmark_extractor.extract_bookmarks(with_content=False)
    save_bookmarks_to_cache(bookmarks)  # Save new bookmarks to cache
elif cached_bookmarks:
    st.info("📌 Loaded cached bookmarks.")
    bookmarks = cached_bookmarks

# Button to trigger clustering
if st.button("🔄 Cluster Bookmarks"):
    start_time = time.time()
    st.session_state.clusters = asyncio.run(bookmark_processor.get_clusters(bookmarks))
    st.session_state.clustered_urls = asyncio.run(bookmark_processor.assign_cluster(bookmarks, st.session_state.clusters))
    
    # Assign clusters to bookmarks
    for bookmark in bookmarks:
        bookmark.cluster = st.session_state.clustered_urls.get(bookmark.url, "Unassigned")
    
    st.session_state.filtered_bookmarks = bookmarks  # Default to all bookmarks
    save_bookmarks_to_cache(bookmarks)  # Save clustered bookmarks

    end_time = time.time()
    st.success(f"✅ Clustering completed in {end_time - start_time:.2f} seconds.")
    st.write(f"🔍 **Total Clustered URLs:** {sum(len(v) for v in st.session_state.clustered_urls.values())}")

# Dropdown for cluster selection
if st.session_state.clusters:
    selected_cluster = st.selectbox("📂 Filter by Cluster:", ["All"] + st.session_state.clusters)

    # Filter bookmarks by cluster
    if selected_cluster != "All":
        filtered_bookmarks = [b for b in bookmarks if b.cluster == selected_cluster]
    else:
        filtered_bookmarks = bookmarks

    # Optional: Filter by added_date
    added_date_values = sorted({b.added_date for b in filtered_bookmarks if b.added_date})
    if added_date_values:
        min_date, max_date = st.slider("📅 Filter by Date:", min_value=min(added_date_values), max_value=max(added_date_values), value=(min(added_date_values), max(added_date_values)))
        filtered_bookmarks = [b for b in filtered_bookmarks if min_date <= b.added_date <= max_date]

    st.session_state.filtered_bookmarks = filtered_bookmarks  # Save filtered bookmarks

# Display cards if bookmarks exist
if st.session_state.filtered_bookmarks:
    show_cards(st.session_state.filtered_bookmarks)
else:
    show_cards(bookmarks)


