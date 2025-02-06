from config import Config
from data_extractor import Bookmark

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from pydantic import BaseModel
from typing import List

class LabelerResponse(BaseModel):
    labels: str

class LabelerDeps(BaseModel):
    bookmark: Bookmark
    labels: str

labeler_agent = Agent(
    model=OpenAIModel('gpt-4o-mini', api_key=Config.OPENAI_KEY),
    # deps type is wrong
    deps_type=LabelerDeps,
    result_type=LabelerResponse,
    model_settings={'temperature':0},
    system_prompt=(
        """
        Decide which labels are the most relevant to the saved bookmark. This is a multiclassification task. Return the predicted labels in one line seperated by commas.
        """
    ),
)

@labeler_agent.system_prompt
async def add_url(ctx: RunContext[LabelerDeps]) -> str:
    return f"Labels: {ctx.deps.labels}\nBoomark URL: {ctx.deps.bookmark.url}\nBookmark Title: {ctx.deps.bookmark.title}\nBookmark Content: {ctx.deps.bookmark.md_content}"

class LabelGeneratorResponse(BaseModel):
    labels: str

label_generator_agent = Agent(
    model=OpenAIModel('gpt-4o-mini', api_key=Config.OPENAI_KEY),
    deps_type=List[Bookmark],
    result_type=LabelGeneratorResponse,
    model_settings={'temperature':0},
    system_prompt=(
        """
        Generate labels covering a wide range of use cases relevant to the following URLs in order to organize them.Return the predicted labels in one line seperated by commas.
        """
    ),
)

@label_generator_agent.system_prompt
async def add_url(ctx: RunContext[List[Bookmark]]) -> str:
    #bookmarks_amount = len(ctx.deps)
    prompt = ''
    for bookmark in ctx.deps:
        prompt += f"Title: {bookmark.title}, URL: {bookmark.url}\n"

    return prompt

class URLSummaryResponse(BaseModel):
    llm_description: str

url_summary_agent = Agent(
    model=OpenAIModel('gpt-4o-mini', api_key=Config.OPENAI_KEY),
    deps_type=Bookmark,
    result_type=URLSummaryResponse,
    model_settings={'temperature':0},
    system_prompt=(
        """
        Generate a detailed description with maximum 150 words.
        """
    ),
)

@url_summary_agent.system_prompt
async def add_url(ctx: RunContext[Bookmark]) -> str:
    return f"URL: {ctx.deps.url}\nTitle: {ctx.deps.title}\nMarkdown Content: {ctx.deps.md_content}"

class URLReductionResponse(BaseModel):
    reduced_url: str
    summary: str

url_reduction_agent = Agent(
    model=OpenAIModel('gpt-4o-mini', api_key=Config.OPENAI_KEY),
    deps_type=str,
    result_type=URLReductionResponse,
    model_settings={'temperature':0},
    system_prompt=(
        """
        Extract the semantically useful part of the URL and provide a concise summary.
        Respond in JSON format with 'reduced_url' and 'summary'.
        """
    ),
)

@url_reduction_agent.system_prompt
async def add_url(ctx: RunContext[str]) -> str:
    return f"URL: {ctx.deps}"

class BookmarkSearchResponse(BaseModel):
    id: int
    relevance_score: float
    reason: str

class BookmarkSearchResponses(BaseModel):
    response: List[BookmarkSearchResponse]

class BookmarkData(BaseModel):
    id: int
    reduced_url: str

class BookmarkSearchDeps(BaseModel):
    deps: List[BookmarkData]

bookmark_search_agent = Agent(
    model=OpenAIModel('gpt-4o-mini', api_key=Config.OPENAI_KEY),
    deps_type=BookmarkSearchDeps,
    result_type=BookmarkSearchResponses,
    model_settings={'temperature':0},
    system_prompt=(
        """
        You are a search assistant. Based on the query, give a relevance_score to the URLs below and a short reason for the score.
        """
    ),
)

@bookmark_search_agent.system_prompt
async def create_url_list(ctx: RunContext[BookmarkSearchDeps]) -> str:
    url_list = "List of URLs:\n"
    for bookmark in ctx.deps:
        url_list += bookmark["reduced_url"] + "\n"
    return url_list