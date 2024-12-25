from config import Config

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from pydantic import BaseModel

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