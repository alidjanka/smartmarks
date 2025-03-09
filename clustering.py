from config import Config
from data_extractor import Bookmark

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from pydantic import BaseModel
from typing import List

class ClusterNames(BaseModel):
    cluster_names: List[str]

cluster_agent = Agent(
    model=OpenAIModel('gpt-4o-mini', api_key=Config.OPENAI_KEY),
    deps_type=List[Bookmark],
    result_type=ClusterNames,
    model_settings={'temperature':0, 'max_completion_tokens':3000},
    system_prompt=(
        """
        You are an URL organizer and your job is to cluster the URLs into meaningful groups. 
        """
    ),
)

@cluster_agent.system_prompt
async def add_url(ctx: RunContext[List[Bookmark]]) -> str:
    #bookmarks_amount = len(ctx.deps)
    prompt = ''
    for bookmark in ctx.deps:
        prompt += f"Title: {bookmark.title}, URL: {bookmark.url}\n"

    return prompt

class ClusteredURL(BaseModel):
    cluster_name: str

cluster_assigner = Agent(
    model=OpenAIModel('gpt-4o-mini', api_key=Config.OPENAI_KEY),
    deps_type=Bookmark,
    result_type=ClusteredURL,
    model_settings={'temperature':0, 'max_completion_tokens':3000},
    system_prompt=(
        """
        You are an URL organizer and your job is to cluster the URLs into meaningful groups. 
        """
    ),
)

@cluster_assigner.system_prompt
async def add_url(ctx: RunContext[Bookmark]) -> str:
    return f"Title: {ctx.deps.title}, URL: {ctx.deps.url}\n"